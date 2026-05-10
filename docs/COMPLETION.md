# Shell Autocompletion

**rt** ships with native shell autocompletion powered by [argcomplete](https://github.com/kislyuk/argcomplete).  
Once enabled, you can press `<TAB>` to discover commands, subcommands, flags, and (where applicable) dynamic values.

## Prerequisites

- **rt** must be installed in your environment (`pip install -e .` or from **PyPI**).
- The optional dependency `argcomplete` is required. Install it alongside **rt**:

```bash
uv sync --group completion
```

If you installed **rt** without the extra, you can add it manually:

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

· The completion command outputs a shell script that hooks into your shell’s completion system.
· The script uses argcomplete to invoke **rt** internally with the _ARGCOMPLETE environment variable set.
· During completion, **rt** skips heavy initialisation (the application container and router are not created), ensuring fast `<TAB>` responses.
· A special `RAZTODO_COMPLETION` guard makes subparsers optional during completion, preventing unnecessary errors.

### Available Commands
```bash
rt completion bash 
rt completion zsh 
rt completion fish
```

---

## Troubleshooting

rt completion bash outputs a script, but `<TAB>` does nothing.

You only printed the script. You must activate it with `eval "$(rt completion bash)"` or `source <(...)`.
Without eval/source, the shell does not register the completion handler.

rt: command not found when pressing `<TAB>`.

Make sure **rt** is in your **PATH**. If you installed with `pip install --user`, ensure `~/.local/bin` is added to **PATH**.
If you use `python -m raztodo`, replace rt with `python -m raztodo` in the eval command:

```bash
eval "$(python -m raztodo completion bash)"
```

Completion works but is slow.

Completion should be fast because the application container is not bootstrapped.
If you experience slowness, check that you are using the latest version of argcomplete (≥3.0).

argcomplete not found.

Install it:

```bash
pip install argcomplete
```

Or reinstall **rt** with the completion extra.

Uninstalling Completion

Remove the eval line from your shell’s configuration file `~/.bashrc` , `~/.zshrc` and restart your shell.
For Fish, delete the file `~/.config/fish/completions/rt.fish`.