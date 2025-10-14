import typer

from src.cli.commands.start import start as start_impl
from src.cli.commands.status import status as status_impl
from src.cli.commands.stop import stop as stop_impl
from src.cli.commands.clean import clean as clean_impl

app = typer.Typer()


@app.command()
def start():
    start_impl(path="./test/fake_project/easyfed.yaml")


@app.command()
def status():
    status_impl(path="./test/fake_project/easyfed.yaml")


@app.command()
def stop():
    stop_impl(path="./test/fake_project/easyfed.yaml")


@app.command()
def clean():
    clean_impl(path="./test/fake_project/easyfed.yaml")
