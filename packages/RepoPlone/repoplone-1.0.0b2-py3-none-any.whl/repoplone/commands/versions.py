from repoplone import _types as t
from repoplone.app import RepoPlone
from repoplone.utils import display as dutils
from repoplone.utils import versions as vutils

import typer


app = RepoPlone()


@app.command()
def current(ctx: typer.Context):
    """Report versions of all components of this repository."""
    settings: t.RepositorySettings = ctx.obj.settings
    cur_versions = vutils.report_cur_versions(settings)
    title = "Current versions"
    cols = [{"header": "Section"}, {"header": "Name"}, {"header": "Version"}]
    rows = [
        (section["title"], section["name"], section["version"])
        for section in cur_versions["sections"]
    ]
    table = dutils.table(title, cols, rows)
    dutils.print(table)


@app.command()
def dependencies(ctx: typer.Context):
    """Report versions of major dependencies."""
    settings: t.RepositorySettings = ctx.obj.settings
    cur_versions = vutils.report_deps_versions(settings)
    title = "Dependencies versions"
    cols = [{"header": "Section"}, {"header": "Name"}, {"header": "Version"}]
    rows = [
        (section["title"], section["name"], section["version"])
        for section in cur_versions["sections"]
    ]
    table = dutils.table(title, cols, rows)
    dutils.print(table)


@app.command(name="next")
def next_version(ctx: typer.Context):
    """Report next version of all components of this repository."""
    settings: t.RepositorySettings = ctx.obj.settings
    versions = vutils.report_next_versions(settings)
    title = "Possible next version"
    cols = [
        {"header": "Current Version"},
        {"header": "Desired Version"},
        {"header": "Repository"},
        {"header": "Backend"},
        {"header": "Frontend"},
    ]
    rows = [
        (
            settings.version,
            version["bump"],
            version["repository"],
            version["backend"],
            version["frontend"],
        )
        for version in versions
    ]
    table = dutils.table(title, cols, rows)
    dutils.print(table)
