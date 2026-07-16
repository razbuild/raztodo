# Explain a Task with LLM

Use a locally-running [Ollama](https://ollama.com) model to analyse or plan a task.
The task's full data (title, description, priority, due date, tags, project) is passed
to the model as JSON. No data leaves your machine.

```bash
rt explain <id> [mode] [options]
```

## Modes

Mutually exclusive, default: `--short`.

| Flag | Description |
|------|-------------|
| `--short` | 2–3 sentence plain-language summary (default) |
| `--deep` | In-depth analysis: goal, blockers, approach, risks |
| `--plan` | Numbered step-by-step action plan with a time estimate |

## Other Options

| Option | Description |
|--------|-------------|
| `--config` | View or update Ollama settings (no task ID needed) |
| `--model NAME` | Set the model to use (used with `--config`) |
| `--host URL` | Set the Ollama server URL (used with `--config`) |
| `--timeout SECONDS` | Set the request timeout (used with `--config`) |
| `--system-prompt TEXT` | Override the default system prompt (used with `--config`) |
| `--json` | Output result or config as JSON |

## Examples

```bash
# Explain task 5 with a short summary
rt explain 5

# Deep analysis of task 12
rt explain 12 --deep

# Step-by-step plan for task 3
rt explain 3 --plan

# JSON output (useful for scripting)
rt explain 7 --short --json
```

## Requirements

`explain` requires Ollama to be running locally and a model to be configured.
There is no default model, you must set one before first use.

Install Ollama from [ollama.com](https://ollama.com), pull a model, then configure it:

```bash
ollama serve                                            # start the server (or run the desktop app)
ollama pull qwen2.5-coder:3b                            # download a model
rt explain --config --model qwen2.5-coder:3b            # tell RazTodo which model to use
```

If you run `rt explain` without configuring a model first, you will see:

```
usage: raztodo explain [-h] [--short | --deep | --plan] [--config] [--model NAME] [--host URL] [--timeout SECONDS] [--system-prompt TEXT] [--json] [id]
raztodo explain: error: the following arguments are required: id (or use --config)
```

## Configuration

Settings are stored in a JSON file in the RazTodo data directory:

| Platform | Path |
|----------|------|
| Linux / BSD | `~/.local/share/raztodo/llm.json` |
| macOS | `~/Library/Application Support/raztodo/llm.json` |
| Windows | `%APPDATA%\raztodo\llm.json` |

The file is created on first save. Before that, built-in defaults are used.

**View current config:**

```bash
rt explain --config
rt explain --config --json
```

Example output:

```
Ollama config  [/home/raz/.local/share/raztodo/llm.json  not created yet (using defaults)]

  model         qwen2.5-coder:3b
  host          http://localhost:11434
  timeout       120s
  system_prompt You are a helpful productivity assistant. The user will give…

To update: rt explain --config --model <name> --host <url>
```

**Update config:**

```bash
# Change model
rt explain --config --model mistral

# Change model and timeout
rt explain --config --model qwen2.5-coder:3b --timeout 180

# Change server URL (e.g. Ollama running in Docker)
rt explain --config --host http://localhost:11434

# Override the system prompt
rt explain --config --system-prompt "You are a senior software engineer."
```

## Environment Variables

Environment variables take precedence over the config file and are useful
for one-off overrides or CI environments:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server base URL |
| `OLLAMA_MODEL` | `None` | Model name |
| `OLLAMA_TIMEOUT` | `120` | Request timeout in seconds |

```bash
OLLAMA_MODEL=qwen2.5-coder:3b rt explain 5 --deep
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot connect to Ollama` | Server not running | Run `ollama serve` or start the Ollama desktop app |
| `Model 'X' not found` | Model not downloaded | Run `ollama pull X` |
| `Ollama returned HTTP 404` | Wrong model name | Run `ollama list` to see available models, then `rt explain --config --model <name>` |
| Slow response | Large model or low-end hardware | Try a smaller model (`ollama pull mistral`) or increase `--timeout` |

## Web UI

If you install the optional `web` extra, the local web UI (`rt-web`) also includes an
**Explain** button on each task that opens a modal with the same three modes
(Summary, Deep Analysis, Action Plan). Responses stream in token-by-token, so you see
output immediately as the model generates it. Ollama must be configured and running
for this feature to work, following the same setup instructions above.