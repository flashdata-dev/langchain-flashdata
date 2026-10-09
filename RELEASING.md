# Publishing langchain-flashdata

Source publication, PyPI publication, a LangChain listing request, and acceptance
into the official directory are separate milestones. Version 0.1.0 is prepared;
the initial PyPI publication still requires a PyPI publishing identity.

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

Create or use a FlashData-controlled [PyPI account](https://pypi.org/account/register/),
verify its email and enable two-factor authentication. Keep passwords, recovery
codes and one-time codes with the account owner.

For the first publication, add a **pending publisher** at
<https://pypi.org/manage/account/publishing/> with these exact values:

| Field | Value |
| --- | --- |
| PyPI project name | `langchain-flashdata` |
| Owner | `flashdata-dev` |
| Repository | `langchain-flashdata` |
| Workflow filename | `publish.yml` |
| GitHub environment | `pypi` |

Create the corresponding `pypi` GitHub environment and restrict release access as
appropriate. The workflow uses GitHub OIDC, so no long-lived PyPI token is needed.
This publisher authorizes this repository/workflow to publish future releases of
this package; it is not an npm or GitHub login.

After the publisher exists, tag the verified main commit `v0.1.0`, push the tag,
and manually run **Publish to PyPI** with that tag selected. The workflow checks
that the tag matches the package version, tests, builds, and publishes exactly the
built wheel and source archive. It will not publish from a branch. Do not overwrite
a released version or retry an uncertain publication without checking PyPI first.

After success, verify <https://pypi.org/project/langchain-flashdata/> and install
`langchain-flashdata==0.1.0` in a clean environment. Update README installation to
the PyPI command, remove the pending publication note, and record the release
date, workflow URL and artifact hashes in the GTM task.

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
