import os
from typing import List
import typer
import UVR

app = typer.Typer()


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


@app.command()
def process(input_files: List[str], output_dir: str):
    _validate_paths(input_files, output_dir)
    root = UVR.MainWindow(is_cli=True)
    UVR.set_root(root)

    root.inputPaths = input_files
    root.process_input_selections()
    root.update_inputPaths()

    root.export_path_var.set(os.path.join(output_dir))

    root.process_start()
    raise typer.Exit()


@app.callback()
def main(
    input_files: List[str] = typer.Option(..., help="List of input files"),
    output_dir: str = typer.Option(..., help="Output directory")
):
    process(input_files, output_dir)


if __name__ == "__main__":
    app()
