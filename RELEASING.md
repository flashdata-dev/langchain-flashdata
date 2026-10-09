# Publishing langchain-flashdata

Source publication, PyPI publication, a LangChain listing request, and acceptance
into the official directory are separate milestones. PyPI publication uses the
configured GitHub Trusted Publisher. Version 0.1.0 was first published on
2026-10-09; version 0.1.1 updates the published installation documentation.

## Verify the release

```bash
uv sync --frozen --extra examples
uv run --extra examples pytest --disable-socket --allow-unix-socket
uv run ruff check .
uv run ruff format --check .
uv build
uv run twine check dist/*
```

Live tests are opt-in and consume credits. Run them for relevant API changes;
do not repeat them merely to recreate a release artifact.

## PyPI Trusted Publisher

The publisher is already configured under the FlashData-controlled PyPI account
`flashdata-dev`, with verified email and two-factor authentication. Keep
passwords, recovery codes and one-time codes with the account owner.

The first publication used a pending publisher, now bound to the created project.
Manage it at <https://pypi.org/manage/project/langchain-flashdata/settings/publishing/>.
Do not create another pending publisher for this existing package. Its settings are:

| Field | Value |
| --- | --- |
| PyPI project name | `langchain-flashdata` |
| Owner | `flashdata-dev` |
| Repository | `langchain-flashdata` |
| Workflow filename | `publish.yml` |
| GitHub environment | `pypi` |

The corresponding `pypi` GitHub environment exists. The workflow uses GitHub OIDC,
so no long-lived PyPI token is needed.
This publisher authorizes this repository/workflow to publish future releases of
this package; it is not an npm or GitHub login.

For each release, update the version in `pyproject.toml`, `uv.lock`, and the
package user agent, then verify the release and merge its changes. Tag the
verified main commit (for example `v0.1.1`), push the tag,
and manually run **Publish to PyPI** with that tag selected. The workflow checks
that the tag matches the package version, tests, builds, and publishes exactly the
built wheel and source archive. It will not publish from a branch. Do not overwrite
a released version or retry an uncertain publication without checking PyPI first.

After success, verify <https://pypi.org/project/langchain-flashdata/> and install
the exact released version in a clean environment. Record the release date,
workflow URL and artifact hashes in the GTM task. Package descriptions on PyPI
come from the built README: verify the installation command and absolute
documentation links before building, because released metadata is immutable.

## LangChain official listing

After PyPI publication, use the [official Integration listing form](https://github.com/langchain-ai/docs/issues/new?template=06-integration-submission.yml).
The prepared form body is [docs/langchain-listing.md](docs/langchain-listing.md).
Check the published-package confirmation only after PyPI has been verified.

A maintainer applies `integration-run`; the automation creates the documentation
PR. Do not manually open a new listing PR unless asked by a maintainer. New
packages normally receive an external listing linking to this README, rather
than a full guide hosted by LangChain. Monitor the same issue/PR for feedback;
do not repeatedly tag maintainers or create duplicate submissions.

The authoritative process is [Publish an integration](https://docs.langchain.com/oss/python/contributing/publish-langchain),
verified on 2026-10-09. Verify it again before submitting if the process changes.
