import os
from typing import List
import typer
import UVR

app = typer.Typer()


@app.callback()
def main(
        input_files: List[str] = typer.Option(..., help="List of input files"),
        output_dir: str = typer.Option(..., help="Output directory"),
        is_gpu_conversion: bool = typer.Option(is_flag=True, default=False, help="Should use GPU to perform conversion"),
        is_only_vocals: bool = typer.Option(is_flag=True, default=False, help="Should only save vocals"),
):
    process(input_files, output_dir, is_gpu_conversion, is_only_vocals)


@app.command()
def process(input_files: List[str], output_dir: str, is_gpu_conversion: bool, is_only_vocals: bool):
    input_files, output_dir_path = _validate_paths(input_files, output_dir)
    should_emulate_display = True if os.getenv('UVR_emulate_display') is not None else False
    root = UVR.MainWindow(is_cli=True, should_emulate_display=should_emulate_display)
    # Need to do this, as a lot of state is global (e.g. new objects refer to state in `root` on init ...)
    UVR.set_root(root)

    # TODO - This nonsense is due to the fact that some settings are being 'wiped'
    # when running with virtual display, suspect the TK lib is relying on the GUI to
    # refresh some data? Hence the CLI falls over, unless we manually set things *again*?
    # TODO - When running locally (e.g. not in headless) this list loads correctly, so we can
    # diff to see the difference between docker and local (yay).
    _apply_setting(root, input_files, output_dir_path, is_gpu_conversion, is_only_vocals)

    root.process_start()
    raise typer.Exit()


def _apply_setting(root: UVR.MainWindow, input_files: list[str], output_dir_path: str, is_gpu_conversion: bool, is_only_vocals: bool):
    root.command_Text.write(f'Loaded settings: {root.get_settings_list()}')
    root.command_Text.write(f'Applying settings from CLI ...')

    root.mdx_net_model_var.set('UVR-MDX-NET Inst HQ 1')
    # TODO - No idea how we actually select GPUs, I guess just assume always 1?
    root.is_gpu_conversion_var.set(int(is_gpu_conversion is True))
    root.save_format_var.set('MP3')
    if is_only_vocals:
        root.command_Text.write(UVR.VOCAL_STEM_ONLY)
        root.is_secondary_stem_only_Text_var.set(UVR.VOCAL_STEM_ONLY)
        root.is_secondary_stem_only_var.set(True)
    else:
        # TODO - Confirm is this makes sense...
        root.is_secondary_stem_only_var.set(False)
    root.command_Text.write(f'Resulting settings for conversion: {root.get_settings_list()}')

    _set_input(input_files, root)
    root.export_path_var.set(output_dir_path)


def _set_input(input_files: list[str], root: UVR.MainWindow):
    root.inputPaths = input_files
    root.process_input_selections()
    root.update_inputPaths()


# TODO - ... fairly sure can hook this to Typer directly?
def _validate_paths(input_files: List[str], output_dir: str):
    output_dir_path = os.path.join(output_dir)
    if not os.path.isdir(output_dir_path):
        typer.echo(f"'--output-dir' argument [{output_dir}] is not a directory")
        raise typer.Exit()
    if not os.path.exists(output_dir_path):
        typer.echo(f"'--output-dir' argument [{output_dir}] does not exist")
        raise typer.Exit()

    for input_file in input_files:
        input_file_path = os.path.join(input_file)
        if not os.path.isfile(input_file_path):
            typer.echo(f"'--input-files' argument [{input_file}] is not a file")
            raise typer.Exit()
        if not os.path.exists(input_file_path):
            typer.echo(f"'--output-dir' argument [{input_file}] does not exist")
            raise typer.Exit()

    return input_files, output_dir_path


if __name__ == "__main__":
    app()
