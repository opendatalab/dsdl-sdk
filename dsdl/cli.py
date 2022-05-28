import click

from dsdl import parse


@click.group()
def cli():
    pass


cli.add_command(parse)


if __name__ == "__main__":
    cli()
