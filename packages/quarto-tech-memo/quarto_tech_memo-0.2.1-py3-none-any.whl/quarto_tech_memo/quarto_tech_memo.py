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
def tasks1(md_file: str = typer.Argument(..., help="markdown note to convert"), 
           to: Format=typer.Option("memo1", help="Choose format"), preview: bool=False):
    print(f"Converting markdown note {md_file} to format {to.value}")


    # Adjust format for quarto
    to = to.value + ("-typst" if to.value!="ieee" else "-pdf")

        
    # Ensure quarto-tech-memo extension is installed
    src=Path(md_file)
    if not (src.parent/"_extensions/gael-close").exists():
        with change_dir(src.parent):
            print("Installing quarto-tech-memo extension")    
            subprocess.run("quarto add gael-close/quarto-tech-memo --no-prompt --quiet", shell=True)
            
    # Render the markdown file to the specified format
    if preview:
        subprocess.run(f"quarto preview {md_file} --to {to}", shell=True)
    else:
        subprocess.run(f"quarto render {md_file} --to {to}", shell=True)
    
if __name__ == "__main__":
    app()