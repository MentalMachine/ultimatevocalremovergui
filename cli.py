import os
from typing import List
import typer
import UVR

app = typer.Typer()

# TODO - There is another, but these are all I care about for now.
SUPPORTED_OUTPUT_FORMATS = ["WAV", "MP3"]

@app.callback()
def main(
        input_files: List[str] = typer.Option(..., help="List of input files"),
        output_dir: str = typer.Option(..., help="Output directory"),
        output_format: str = typer.Option(default="WAV", help="Output directory"),
        is_gpu_conversion: bool = typer.Option(is_flag=True, default=False, help="Should use GPU to perform conversion"),
        is_vocals_only: bool = typer.Option(is_flag=True, default=False, help="Should only save vocals"),
        is_instrumentals_only: bool = typer.Option(is_flag=True, default=False, help="Should only save instrumentals"),
):
    process(input_files, output_dir, output_format, is_gpu_conversion, is_vocals_only, is_instrumentals_only)


@app.command()
def process(input_files: List[str], output_dir: str, output_format, is_gpu_conversion: bool, is_vocals_only: bool, is_instrumentals_only: bool):
    input_files, output_dir_path, output_format = _validate_args(input_files, output_dir, output_format, is_vocals_only ,is_instrumentals_only)
    should_emulate_display = True if os.getenv('UVR_emulate_display') is not None else False
    root = UVR.MainWindow(is_cli=True, should_emulate_display=should_emulate_display)
    # Need to do this, as a lot of state is global (e.g. new objects refer to state in `root` on init ...)
    UVR.set_root(root)

    _apply_setting(root, input_files, output_dir_path, output_format, is_gpu_conversion, is_vocals_only, is_instrumentals_only)

    root.process_start()
    _cleanup(root)
    raise typer.Exit()


def _apply_setting(root: UVR.MainWindow, input_files: list[str], output_dir_path: str, output_format: str, is_gpu_conversion: bool, is_vocals_only: bool, is_instrumentals_only: bool):
    # In docker, we do not copy across any local `data.pkl` file, so we will load the
    # default settings (see `gui_data/constants.py` -> `DEFAULT_DATA`) first, then "apply" what we want.
    # Alternatively, a manually curated `data.pkl` can be made via the GUI, then mounted it and then tweaked as needed.
    root.command_Text.write(f'Loaded settings: {root.get_settings_list()}')
    root.command_Text.write(f'Applying settings from CLI ...')

    # Filename on disk is `UVR-MDX-NET-Inst_HQ_1.onnx`.
    # TODO - Inst HQ 1 has `Inst... Only` and then `Vocals Only`, but MDX23C is the opposite, so hence why
    # it is primary vs secondary. Segment Size and Overlap also have different "bases". so CLI is going
    # to get busy very fast (especially if want ensemble mode, which.... yikes).
    root.mdx_net_model_var.set('UVR-MDX-NET Inst HQ 1')
    # TODO - No idea how we actually select GPUs, I guess just assume always 1?
    root.is_gpu_conversion_var.set(int(is_gpu_conversion is True))
    root.save_format_var.set(output_format)

    # Reset these to ensure we honour CLI args, and do not get stuck in state when loading
    # the 'data.pkl'
    root.is_primary_stem_only_var.set(False)
    root.is_secondary_stem_only_var.set(False)
    if is_vocals_only:
        # TODO - Think the exact text might be model specific? And the GUI has to do this odd pattern
        # to confirm that?
        root.is_secondary_stem_only_Text_var.set(UVR.VOCAL_STEM_ONLY)
        root.is_secondary_stem_only_var.set(True)
    elif is_instrumentals_only:
        # TODO - No idea where this string is coming from/defined
        root.is_primary_stem_only_Text_var.set('Instrumental Only')
        root.is_primary_stem_only_var.set(True)
    root.command_Text.write(f'Resulting settings for conversion: {root.get_settings_list()}')

    _set_input(input_files, root)
    root.export_path_var.set(output_dir_path)


def _cleanup(root: UVR.MainWindow):
    root.is_primary_stem_only_var.set(False)
    root.is_secondary_stem_only_var.set(False)
    root.save_values()


def _set_input(input_files: list[str], root: UVR.MainWindow):
    root.inputPaths = input_files
    root.process_input_selections()
    root.update_inputPaths()


# TODO - ... fairly sure can hook this to Typer directly?
def _validate_args(input_files: List[str], output_dir: str, output_format: str, is_vocals_only: bool, is_instrumentals_only: bool):
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

    if output_format not in SUPPORTED_OUTPUT_FORMATS:
        typer.echo(f"'--output-format' argument [{output_format}] not supported, must be one of {SUPPORTED_OUTPUT_FORMATS}")
        raise typer.Exit()

    if is_instrumentals_only and is_vocals_only:
        typer.echo(f"'Cannot run with both '--is-vocals-only' and '--is-instrumentals-only'; these options are mutually exclusive")
        raise typer.Exit()

    return input_files, output_dir_path, output_format


if __name__ == "__main__":
    app()
