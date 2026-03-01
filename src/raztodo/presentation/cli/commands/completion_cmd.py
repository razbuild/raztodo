import os
os.environ["RAZTODO_COMPLETION"] = "1"

# Precompute a static command list for instant completions
COMMANDS = "add list update done remove search export import migrate clear completion"

class CompletionCMD:
    def __init__(self, get_task_ids=None):
        # `get_task_ids` can be used later for dynamic task ID completions
        self.get_task_ids = get_task_ids

    def __call__(self, shell: str):
        try:
            if shell in ["bash", "zsh"]:
                # Minimal argcomplete shellcode; no router or use case initialization
                import argcomplete
                print(argcomplete.shellcode(shell=shell, executables=["rt"]))
                return 0

            elif shell == "fish":
                # Static command list; lightning-fast
                task_ids_str = ""  # can later be dynamically filled
                print(f"""
function __rt_complete
    set -l cmd (commandline -opc)
    echo {COMMANDS} {task_ids_str}
end

complete -c rt -f -a '(__rt_complete)'
""")
                return 0

            else:
                print(f"Unsupported shell: {shell}")
                return 1

        except Exception as e:
            print("[✗] Unexpected error:", e)
            return 1


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "completion",
        help="Output shell completion script for bash, zsh, or fish"
    )
    parser.add_argument(
        "shell",
        choices=["bash", "zsh", "fish"],
        help="Shell type for completion"
    )
    return parser