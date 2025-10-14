## DSPy Hub

DSPy Hub is the home for shareable DSPy programs. It powers
[dspyhub.com](https://dspyhub.com) with:

- A Python SDK (`dspy_hub`) that can load and publish packages programmatically.
- A CLI (`dspy-hub`) for browsing registries and installing packages locally.
- A Cloudflare Worker backend that reads and writes packages to an R2 bucket.
- A modern React frontend for discovery, login, and authoring workflows.

### Developer experience

- **Read for free** – anyone can explore packages with the browser UI, CLI, or SDK.
- **Authenticated publishing** – writing back to the hub requires a developer key. Provide it
  via the `DSPY_HUB_DEV_KEY` environment variable (CLI/SDK) or sign in through the frontend.
- **Multiple surfaces** – use the CLI for quick installs, the SDK for automation, or the web UI
  for curated browsing and author insights.

---

## Python SDK

```python
import dspy
import dspy_hub

# Build an optimized program locally
people_extractor = dspy.ChainOfThought(PeopleExtraction)

# Publish it to DSPy Hub (requires DSPY_HUB_DEV_KEY)
package_metadata = {
    "author": "Kevin Madura",
    "model": "openai/gpt-4.1-mini",
    "optimizer": "MIPROv2",
    "date": "2025-10-11",
    "version": "0.1.0",
    "tags": ["example", "starter"],
}
dspy_hub.save_program_to_hub("dspy-team/people-extractor", people_extractor, package_metadata)

# Load it back, ready to invoke
loaded_extractor = dspy_hub.load_program_from_hub(
    "dspy-team/people-extractor",
    lambda: dspy.ChainOfThought(PeopleExtraction),  # zero-arg factory that instantiates the module
)
print(loaded_extractor(tokens=["Italy", "recalled", "Marcello", "Cuttitta"]).extracted_people)
```

Need raw access to manifests or files? Reach for the lower-level helpers:

```python
package = dspy_hub.load_from_hub("dspy-team/people-extractor")
print(package.manifest["metadata"])

dspy_hub.save_to_hub("dspy-team/people-extractor", package, package_metadata)
```


## CLI usage

Install the project in editable mode with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -e .
dspy-hub list
dspy-hub install dspy-team/people-extractor --dest ./dspy_components
```

Packages are addressed as `<author>/<name>`. By default, the CLI reads from the bundled sample
registry located at `dspy_hub/sample_registry/index.json`. Override the registry with
`DSPY_HUB_REGISTRY`, `--registry`, or a config file stored at
`~/.config/dspy-hub/config.json` (Linux/macOS) or its platform equivalent.


## Registry manifest format

Registries expose a JSON manifest with a top-level `packages` array. Each package entry must
provide:

- `name`: package name (unique per author).
- `author`: package namespace (e.g. team or individual).
- `version`: semantic version string.
- `description`: human-friendly summary.
- `files`: list describing which artifacts to install. Each entry requires a `source` (relative
  to the manifest) and optionally a `target` (where it should be written inside the destination
  directory).
- `metadata`: arbitrary structured metadata that will be mirrored by the SDK.

Example (abridged):

```json
{
  "packages": [
    {
      "name": "people-extractor",
      "author": "dspy-team",
      "version": "0.1.0",
      "description": "Optimized DSPy program that extracts individual people tokens from tokenized news wires.",
      "tags": ["example", "nlp", "optimized"],
      "metadata": {
        "author": "Kevin Madura",
        "model": "openai/gpt-4.1-mini",
        "optimizer": "MIPROv2",
        "date": "2025-10-11",
        "dependency_versions": {
          "python": "3.10",
          "dspy": "3.0.3",
          "cloudpickle": "3.1"
        }
      },
      "files": [
        {
          "source": "packages/dspy-team/people-extractor/optimized_program.json",
          "target": "dspy-team/people-extractor/optimized_program.json",
          "sha256": "1406da85d402ffafe5dff70301841b408e70d76064f2e62742296eb3edbdda5a"
        }
      ]
    }
  ]
}
```


## Installation destinations

Packages are copied into a destination folder (default `./dspy_packages`). Each file's `target`
is interpreted relative to that folder. Use `--dest` to override and `--force` to overwrite
pre-existing files.

```bash
dspy-hub install dspy-team/people-extractor --dest ./dspy_components --force
```


## Cloudflare Worker backend

The `cloudflare/registry-worker` directory contains a Worker that serves the registry and
exposes a write API backed by R2. Reads are anonymous; writes require a bearer token set via the
`WRITE_API_TOKEN` secret. Endpoints:

- `GET /index.json` – aggregated manifest of all packages.
- `GET /api/packages/<author>/<name>` – raw manifest for a single package.
- `PUT /api/packages/<author>/<name>` – publish (requires `Authorization: Bearer …`).

See `cloudflare/registry-worker/README.md` for deployment instructions and seed data.


## Web frontend

`frontend/` hosts the React SPA that powers dspyhub.com. It provides:

- Searchable browsing experience with author/name routes like `/dspy-team/people-extractor`.
- Client-side login: enter your developer key in the header to enable publishing tools.
- Configurable registry endpoint via `VITE_REPOSITORY_ENDPOINT` (defaults to bundled sample).

Refer to `frontend/README.md` for local development and GitHub Pages deployment details.


## Configuration summary

| Environment variable       | Purpose                                       |
| -------------------------- | --------------------------------------------- |
| `DSPY_HUB_REGISTRY`        | Custom registry index (`index.json`) URL.     |
| `DSPY_HUB_CONFIG`          | Override path to the CLI configuration file.  |
| `DSPY_HUB_DEV_KEY`         | Developer key for publishing packages.        |
| `WRITE_API_TOKEN` (Worker) | Secret token authorising write operations.    |


## Sample data

The repository bundles a minimal registry (`dspy_hub/sample_registry`) and matching Cloudflare
seed files under `cloudflare/registry-worker/sample`. They demonstrate the expected directory
layout in R2:

```
metadata/<author>/<package>.json
packages/<author>/<package>/...
```

Use these samples to test end-to-end flows before wiring up your own storage.
