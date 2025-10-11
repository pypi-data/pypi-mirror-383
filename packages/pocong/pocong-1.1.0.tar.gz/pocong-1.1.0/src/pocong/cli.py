"""Console script for pocong."""

import sys

import click

from pocong import __version__


@click.command()
@click.option('--version', 'version', flag_value='version', default=False, help="show current version")
def main(version):
    """Console script for pocong."""
    if version == 'version':
        click.echo('version: '+__version__)  # noqa
    else:
        click.echo("Replace this message by putting your code into pocong.cli.main")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
