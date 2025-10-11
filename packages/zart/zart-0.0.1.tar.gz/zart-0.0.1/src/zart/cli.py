import click

from .lib import remove


@click.group()
def main():
    pass


@main.command()
@click.argument("store")
def rm(store):
    """Remove a Zarr store."""
    remove(store)
