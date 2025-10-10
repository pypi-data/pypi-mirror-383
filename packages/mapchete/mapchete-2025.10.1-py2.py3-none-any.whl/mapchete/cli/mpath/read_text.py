import click

from mapchete.cli import options
from mapchete.path import MPath


@click.command(help="Print contents of file as text.")
@options.arg_path
@options.opt_src_fs_opts
def read_text(path: MPath, **_):
    try:
        click.echo(path.read_text())
    except Exception as exc:  # pragma: no cover
        raise click.ClickException(str(exc))
