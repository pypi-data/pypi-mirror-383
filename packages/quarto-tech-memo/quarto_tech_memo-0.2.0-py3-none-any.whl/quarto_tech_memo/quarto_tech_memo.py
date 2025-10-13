import subprocess
from pathlib import Path
import os
import sys
from contextlib import contextmanager
from enum import Enum
import typer
app=typer.Typer()

@contextmanager
def change_dir(destination):
    prev_dir = os.getcwd()
    os.chdir(destination)
    try:
        yield
    finally:
        os.chdir(prev_dir)


class Format(str, Enum):
    f1 = "memo1"
    f2 = "memo2"
    f3 = "poster"
    f4 = "slides" 
    f5 = "ieee"

@app.command()
def tasks1(arg1: str = typer.Argument(..., help="markdown note to convert"), 
           to: Format=typer.Option("memo1", help="Choose format"), preview: bool=False):
    print(f"Converting markdown note {arg1} to format {to.value}")
    venv_path = Path(sys.executable).parent.parent
    print(f"Using Python from virtual environment at {venv_path}")

    # Adjust format for quarto
    to = to.value + ("-typst" if to.value!="ieee" else "-pdf")

    # Ensure quarto-tech-memo extension is installed
    with change_dir(Path(venv_path)):
        if not (Path(venv_path)/"_extensions/gael-close").exists():
            print("Installing quarto-tech-memo extension")
            subprocess.run("quarto add gael-close/quarto-tech-memo --no-prompt --quiet", shell=True)
    
    # Create symlink to _extensions in the current directory
    try:
        Path('_extensions').symlink_to(f'{venv_path}/_extensions')
    except FileExistsError:
        pass

    # Render the markdown file to the specified format
    if preview:
        subprocess.run(f"quarto preview {arg1} --to {to}", shell=True)
    else:
        subprocess.run(f"quarto render {arg1} --to {to}", shell=True)
    
if __name__ == "__main__":
    app()