import typing as t

from automyte import (
    Automaton,
    Config,
    ContainsFilter,
    File,
    LocalFilesExplorer,
    Project,
    RunContext,
    TasksFlow,
    VCSConfig,
    conditionals,
    flow,
    guards,
)


def lol(ctx: RunContext, file: File | None):
    import re

    if file:
        file.edit(re.sub(r"world", "there", file.get_contents()))


def test_guards_simple(tmp_local_project):
    dir = tmp_local_project(structure={"src": {"hello.txt": "hello world!"}})

    Automaton(
        name="impl1",
        config=Config(vcs=VCSConfig(dont_disrupt_prior_state=False)),
        projects=[
            Project(
                project_id="test_project",
                explorer=LocalFilesExplorer(rootdir=dir, filter_by=ContainsFilter(contains="hello world")),
            ),
        ],
        tasks=TasksFlow(
            [
                flow.If(lol, lol, lol, check=guards.MODE.amend),
            ]
        ),
    ).run()

    with open(f"{dir}/src/hello.txt", "r") as f:
        assert f.read() == "hello world!"
