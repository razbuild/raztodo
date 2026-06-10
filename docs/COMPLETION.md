# Shell Autocompletion

**rt** ships with native shell autocompletion for bash, zsh, and fish. Bash and zsh use [argcomplete](https://github.com/kislyuk/argcomplete); fish uses a lightweight built-in static completion script.
Once enabled, you can press `<TAB>` to discover commands, subcommands, and flags.

## Prerequisites

- **rt** must be installed in your environment (`pip install -e .` or from **PyPI**).
- The optional `completion` extra is required for **bash/zsh** completion support. Fish completion works without it.
- Install the extra alongside **rt** if you want bash/zsh completion:

```bash
pip install "raztodo[completion]"
```

For local development with uv:

```bash
uv sync --extra completion
```

If you prefer, you can also install the underlying package directly:

```bash
pip install argcomplete
```

## Quick Start (Bash)

Enable autocompletion for your current shell session:

```bash
eval "$(rt completion bash)"
```

Now try it out:

```bash
rt <TAB>            # Shows all commands (add, remove, list, …)
rt a<TAB>           # Completes to "add"
rt update --<TAB>   # Shows available flags
```

To make it permanent, add the eval line to your `~/.bashrc`:

```bash
echo 'eval "$(rt completion bash)"' >> ~/.bashrc
source ~/.bashrc
```

## Zsh

Enable for the current session:

```bash
eval "$(rt completion zsh)"
```

For permanent setup, add to `~/.zshrc`:

```bash
echo 'eval "$(rt completion zsh)"' >> ~/.zshrc
source ~/.zshrc
```

> Note: If you use compinit, you may need to ensure it runs after the eval.
> The generated script is compatible with standard Zsh completion.

## Fish

Fish does not use eval. Source the script directly:

```bash
rt completion fish | source
```

To make it permanent, save the script in Fish’s completions directory:

```bash
rt completion fish > ~/.config/fish/completions/rt.fish
```

## How It Works

- `rt completion bash` and `rt completion zsh` output argcomplete-based shell code.
- `rt completion fish` outputs a small built-in completion script and does not require `argcomplete`.
- During completion, RazTodo avoids building the application router, keeping completion startup fast.
- A `RAZTODO_COMPLETION` guard makes subparsers optional during completion.

### Available Commands
```bash
rt completion bash 
rt completion zsh 
rt completion fish
```

---

## Troubleshooting

rt completion bash outputs a script, but `<TAB>` does nothing.

You only printed the script. You must activate it with `eval "$(rt completion bash)"`.
Without eval, the shell does not register the completion handler.

rt: command not found when pressing `<TAB>`.

Make sure **rt** is in your **PATH**. If you installed with `pip install --user`, ensure `~/.local/bin` is added to **PATH**.
If you use `python -m raztodo`, replace rt with `python -m raztodo` in the eval command:

```bash
eval "$(python -m raztodo completion bash)"
```

Completion works but is slow.

Completion should be fast because RazTodo avoids building the full command router during completion.
If you experience slowness with bash/zsh completion, check that you are using a recent version of argcomplete.

argcomplete not found.

Install it:

```bash
pip install "raztodo[completion]"
```

Or install the underlying package directly:

```bash
pip install argcomplete
```

## Uninstalling Completion

Remove the eval line from your shell’s configuration file `~/.bashrc` , `~/.zshrc` and restart your shell.
For Fish, delete the file `~/.config/fish/completions/rt.fish`.