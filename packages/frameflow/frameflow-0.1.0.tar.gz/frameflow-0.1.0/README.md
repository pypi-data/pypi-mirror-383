# FrameFlow

FrameFlow brings TypeScript-style, column-aware type checking to pandas via a mypy plugin. If you reference a missing column (like `df["age"]` when no `"age"` exists), you get a squiggle during type check — not at runtime.

## Install (pick one)

- Recommended (pandas users)
```bash
pip install "frameflow[pandas]"
# uv: uv add "frameflow[pandas]"
```

- Pandera users
```bash
pip install "frameflow[pandera]"
# uv: uv add "frameflow[pandera]"
```

- Already have pandas and pandas-stubs installed
```bash
pip install frameflow
# uv: uv add frameflow
```

- Both integrations
```bash
pip install "frameflow[all]"
# uv: uv add "frameflow[all]"
```

## Enable the plugin

In `mypy.ini` (or `pyproject.toml` under `[tool.mypy]`):

```ini
[mypy]
plugins = frameflow
python_version = 3.12
strict = True

[mypy-pandas.*]
ignore_missing_imports = True

[mypy-pandera.*]
ignore_missing_imports = True
```

You can also use the module path:
```ini
plugins = mypy_frameflow.plugin
```

## Quick start

```python
import pandas as pd

df = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
_ = df["id"]   # OK
_ = df["age"]  # error: column not found: 'age'
```

It understands a few operations and updates the known column set:
- `pd.DataFrame({...})` with a dict literal → seeds columns from keys
- `df.assign(x=...)` → adds columns
- `df.drop(columns=[...])` → removes columns (when literals flow)
- `df[["a","b"]]` with literal strings → narrows to those columns
- `df.rename(columns={"old": "new"})` with a literal dict → renames
- Pandera bridge: `pandera.typing.DataFrame[YourSchema]` seeds from schema fields

## IDE setup

### VS Code

1. Install the **Mypy Type Checker** extension (Pylance/Pyright do not run mypy plugins).
2. Select your interpreter: Command Palette → “Python: Select Interpreter” → choose your project `.venv`.
3. Install the package and extras into that env (using uv):
   ```bash
   uv sync --extra pandas --extra pandera --extra dev
   ```
4. Optional settings in `.vscode/settings.json` (keeps the extension using your env + config):
   ```json
   {
     "mypy-type-checker.importStrategy": "fromEnvironment",
     "mypy-type-checker.args": ["--config-file", "mypy.ini"]
   }
   ```
5. Reload the window. Open a file and you should see live mypy squiggles from FrameFlow.

### PyCharm

1. Install mypy into your project env:
   ```bash
   uv sync --extra dev
   ```
2. Configure mypy as an External Tool (or install a mypy plugin):
   - Program: `./.venv/bin/mypy`
   - Arguments: `--config-file mypy.ini`
   - Working directory: `$ProjectFileDir$`
3. Enable it to run on save/change if available.

### CLI

```bash
uv run mypy path/to/your/code
```

### Troubleshooting

- No squiggles in VS Code: ensure the Mypy extension is installed, the selected interpreter is your project `.venv`, and `plugins = frameflow` is in `mypy.ini`.
- `mypy` not found: run `uv sync --extra dev` or use `uv run mypy ...`.
- Pandas/Pandera types missing: install extras: `uv sync --extra pandas --extra pandera`.

## Notes and limitations

- Only string Literal information is tracked precisely; dynamic `str` variables are treated conservatively.
- Some pandas operations are modeled best-effort; prefer literal forms when you want precise effects on the column set.
- VS Code's Pylance won't display mypy plugin errors; use the Mypy extension for live squiggles.

## License

MIT
