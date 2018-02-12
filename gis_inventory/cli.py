import click
from .inventory import create
from .changes import get_changes

@click.group()
def main():
    pass

main.add_command(create)
main.add_command(get_changes)
