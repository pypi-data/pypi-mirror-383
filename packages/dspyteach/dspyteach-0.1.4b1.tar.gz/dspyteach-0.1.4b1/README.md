# dspyteach – DSPy File Teaching Analyzer

---

[![PyPI](https://img.shields.io/pypi/v/dspyteach.svg?include_prereleases&cacheSeconds=60&t=1)](https://pypi.org/project/dspyteach/)
[![Downloads](https://img.shields.io/pypi/dm/dspyteach.svg?cacheSeconds=300)](https://pypi.org/project/dspyteach/)
[![Python](https.img.shields.io/pypi/pyversions/dspyteach.svg?cacheSeconds=300)](https://pypi.org/project/dspyteach/)
[![License](https://img.shields.io/pypi/l/dspyteach.svg?cacheSeconds=300)](LICENSE)
[![TestPyPI](https://img.shields.io/badge/TestPyPI-dspyteach-informational?cacheSeconds=300)](https://test.pypi.org/project/dspyteach/)
[![CI](https://github.com/AcidicSoil/dspy-file/actions/workflows/release.yml/badge.svg)](…)

---

## DSPy-powered CLI that analyzes source files (one or many) and produces teaching briefs

**Each run captures:**

- an overview of the file and its major sections
- key teaching points, workflows, and pitfalls highlighted in the material
- a polished markdown brief suitable for sharing with learners

The implementation mirrors the multi-file tutorial (`tutorials/multi-llmtxt_generator`) but focuses on per-file inference. The program is split into:

- `dspy_file/signatures.py` – DSPy signatures that define inputs/outputs for each step
- `dspy_file/file_analyzer.py` – the main DSPy module that orchestrates overview, teaching extraction, and report composition. It now wraps the final report stage with `dspy.Refine`, pushing for 450–650+ word briefs.
- `dspy_file/file_helpers.py` – utilities for loading files and rendering the markdown brief
- `dspy_file/analyze_file_cli.py` – command line entry point that configures the local model and prints results. It can walk directories, apply glob filters, and batch-generate briefs.

---

## Requirements

- Python 3.10-3.12+
- DSPy installed in the environment
- A language-model backend. You can choose between:
  - **Ollama** (default): run it locally with the model `hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q6_K_XL` pulled.
  - **LM Studio** (OpenAI-compatible): start the LM Studio server (`lms server start`) and download a model such as `qwen3-4b-instruct-2507@q6_k_xl`.
  - **Any other OpenAI-compatible endpoint**: point the CLI at a hosted provider by supplying an API base URL and key (defaults to `gpt-5`).
- (Optional) `.env` file for DSPy configuration. `dotenv` loads variables such as `DSPYTEACH_PROVIDER`, `DSPYTEACH_MODEL`, `DSPYTEACH_API_BASE`, `DSPYTEACH_API_KEY`, and `OPENAI_API_KEY`.

---

## Example output

[[example-data after running a few passes](example-data/)]

---

Install the Python dependencies if you have not already:
**you dont need all of these commands to correctly install**

### I added multiple install commands and will cleanup later

```bash
uv init

uv venv -p 3.12
source .venv/bin/activate
```

```bash
uv pip install dspy python-dotenv
```

```bash
uv sync
```

#### will add options to use your preferred model of choice later

```bash
ollama pull hf.co/unsloth/Qwen3-4B-Instruct-2507-GGUF:Q6_K_XL
```

```bash
uv pip install dspyteach
```

### Configure the language model

The CLI now supports configurable OpenAI-compatible providers in addition to the default Ollama runtime. You can override the backend via CLI options or environment variables:

```bash
# Use LM Studio's OpenAI-compatible server with its default port
dspyteach path/to/project \
  --provider lmstudio \
  --model qwen3-4b-instruct-2507@q6_k_xl \
  --api-base http://localhost:1234/v1
```

```bash
# Environment variable alternative (e.g. inside .env)
export DSPYTEACH_PROVIDER=lmstudio
export DSPYTEACH_MODEL=qwen3-4b-instruct-2507@q6_k_xl
export DSPYTEACH_API_BASE=http://localhost:1234/v1
dspyteach path/to/project
```

LM Studio must expose its local server before you run the CLI. Start it from the Developer tab inside the LM Studio app or via `lms server start` (see `docs/lm-studio-provider.md` for details); otherwise the CLI will exit early with a connection warning.

**WSL note:** When LM Studio runs on Windows but `dspyteach` runs from WSL, toggle *Serve on local network* in LM Studio's Developer settings so the API binds to `0.0.0.0`. Then point `--api-base` at the Windows host IP (for example `http://<host-ip>:1234/v1`) instead of `localhost`.

For hosted OpenAI-compatible services, set `--provider openai`, supply `--api-base` if needed, and pass an API key either through `--api-key`, `DSPYTEACH_API_KEY`, or the standard `OPENAI_API_KEY`. To keep a local Ollama model running after the CLI finishes, add `--keep-provider-alive`.

## Usage

Run the CLI to extract a teaching brief from a single file:

```bash
dspyteach path/to/your_file
```

You can also point the CLI at a directory. The tool will recurse by default:

```bash
dspyteach path/to/project --glob "**/*.py" --glob "**/*.md"
```

Use `--non-recursive` to stay in the top-level directory, add `--glob` repeatedly to narrow the target set, and pass `--raw` to print the raw DSPy prediction object instead of the formatted report.

### Command examples

- **Personal Example**

  ```bash
  { dt --provider lmstudio -m refactor ./dspy_file/ -ed "prompts/, data/" ;}
  ```

- **Single file (default settings)**

  ```bash
  dspyteach docs/example.md
  ```

- **Directory with multiple glob filters** – quote globs so the shell does not expand them:

  ```bash
  dspyteach ./course-notes --glob "**/*.py" --glob "**/*.md"
  ```

- **Skip subdirectories entirely** – combine with other flags as needed:

  ```bash
  dspyteach ./repo --non-recursive --glob "*.md"
  ```

- **Exclude generated folders** – pass one `--exclude-dirs` per path or provide a comma-separated list with no extra spaces:

  ```bash
  dspyteach ./dspy_file --exclude-dirs prompts/ --exclude-dirs data/
  dspyteach ./dspy_file --exclude-dirs "prompts/,data/"
  ```

  ❌ `dspyteach ./dspy_file -ed prompts/, data/` fails with `unrecognized arguments: data/` because the second path is not attached to `-ed`.
- **Refactor template generation** – switch modes and optionally choose a bundled prompt by name:

  ```bash
  dspyteach ./repo --mode refactor --prompt refactor_prompt_template
  ```

- **Custom prompt file** – works only in refactor mode; ignored otherwise:

  ```bash
  dspyteach ./repo --mode refactor --prompt ./my_prompts/api-hardening.md
  ```

- **Silent raw output for scripting** – useful when piping into other tools:

  ```bash
  dspyteach src/module.py --raw > /tmp/module.teaching.txt
  ```

- **WSL to LM Studio on Windows** – pair the earlier WSL note with a concrete host example:

  ```bash
  dspyteach ./notes \
    --provider lmstudio \
    --api-base http://<windows-host-ip>:1234/v1 \
    --model qwen3-4b-instruct-2507@q6_k_xl
  ```

Need to double-check files before the model runs? Add `--confirm-each` (alias `--interactive`) to prompt before every file, accepting with Enter or skipping with `n`.

To omit specific subdirectories entirely, pass one or more `--exclude-dirs` options. Each value can list comma-separated relative paths (for example `--exclude-dirs "build/,venv/" --exclude-dirs data/raw`). The analyzer ignores any files whose path begins with the provided prefixes.

Prefer short flags? The common options include `-r` (`--raw`), `-m` (`--mode`), `-nr` (`--non-recursive`), `-g` (`--glob`), `-i` (`--confirm-each`), `-ed` (`--exclude-dirs`), and `-o` (`--output-dir`). Mix and match them as needed.

## Refactor files/dirs

Want to scaffold refactor prompt templates instead of teaching briefs? Switch the mode:

```bash
dspyteach path/to/project --mode refactor --glob "**/*.md"
```

---

## Additional Information

The CLI reuses the same file resolution pipeline but feeds each document through the bundled `dspy-file_refactor-prompt_template.md` instructions (packaged under `dspy_file/prompts/`), saving `.refactor.md` files alongside the teaching reports. Teaching briefs remain the default (`--mode teach`), so existing workflows continue to work unchanged.

When multiple templates live in `dspy_file/prompts/`, the refactor mode surfaces a picker so you can choose which one to use. You can also point at a specific template explicitly with `-p/--prompt`, passing either a bundled name (`-p refactor_prompt_template`) or an absolute path to your own Markdown prompt.

Each run only executes the analyzer for the chosen mode. When you pass `--mode refactor` the teaching inference pipeline stays idle, and you can alias the command (for example `alias dspyrefactor='dspyteach --mode refactor'`) if you prefer refactor templates to be the default in your shell.

To change where reports land, supply `--output-dir /path/to/reports`. When omitted the CLI writes to `dspy_file/data/` next to the module. Every run prints the active model name and the resolved output directory before analysis begins so you can confirm the environment at a glance. For backwards compatibility the installer also registers `dspy-file-teaching` as an alias.

Each analyzed file is saved under the chosen directory with a slugged name (e.g. `src__main.teaching.md` or `src__main.refactor.md`). If a file already exists, the CLI appends a numeric suffix to avoid overwriting previous runs.

The generated brief is markdown that mirrors the source material:

- Overview paragraphs for quick orientation
- Section-by-section bullets capturing the narrative
- Key concepts, workflows, pitfalls, and references learners should review
- A `dspy.Refine` wrapper keeps retrying until the report clears a length reward (defaults scale to ~50% of the source word count, with min/max clamps), so the content tends to be substantially longer than a single LM call.
- If a model cannot honour DSPy's structured-output schema, the CLI prints a `Structured output fallback` notice and heuristically parses the textual response so you still get usable bullets.

Behind the scenes the CLI:

1. Loads environment variables via `python-dotenv`.
2. Configures DSPy with the provider selected via CLI or environment variables (Ollama by default).
3. Resolves all requested files, reads contents, runs the DSPy `FileTeachingAnalyzer` module, and prints a human-friendly report for each.
4. Persists each report to the configured output directory so results are easy to revisit.
5. Stops the Ollama model when appropriate so local resources are returned to the pool.

### Extending

- Adjust the `TeachingReport` signature or add new chains in `dspy_file/file_analyzer.py` to capture additional teaching metadata.
- Customize the render logic in `dspy_file.file_helpers.render_prediction` if you want richer CLI output or structured JSON.
- Tune `TeachingConfig` inside `file_analyzer.py` to raise `max_tokens`, adjust the `Refine` word-count reward, or add extra LM kwargs.
- Add more signatures and module stages to capture additional metadata (e.g., security checks) and wire them into `FileAnalyzer`.

---

## Releasing

Maintainer release steps live in [docs/RELEASING.md](docs/RELEASING.md).

## Troubleshooting

- If the program cannot connect to Ollama, verify that the server is running on `http://localhost:11434` and the requested model has been pulled.
- When you see `ollama command not found`, ensure the `ollama` binary is on your `PATH`.
- For encoding errors, the helper already falls back to `latin-1`, but you can add more fallbacks in `file_helpers.read_file_content` if needed.