import re
from collections import defaultdict
from collections.abc import Callable


def display_counts(key: str, depth: int, dl: list[str]) -> None:
    print(f"\n=== {key} ===")
    for d in dl:
        if key not in d:
            print(d["name"])
    cats = [d[key] for d in dl]
    cats = [".".join(re.split(r"\.|, ", c)[:depth]) for c in cats]
    counts = sorted([(cats.count(c), c) for c in sorted(set(cats))], reverse=True)
    for count, item in counts:
        print(f"{count:>4} {item}")


def print_tree(strings):
    # Nested dictionary to hold tree structure
    def tree() -> defaultdict:
        return defaultdict(tree)

    root = tree()

    # Build the tree
    for _string in strings:
        parts = _string.split(".")
        current_level = root
        for part in parts:
            current_level = current_level[part]

    # Function to print the tree recursively
    def print_subtree(node, prefix=""):
        children = list(node.keys())
        for i, child in enumerate(children):
            is_last = i == len(children) - 1
            if is_last:
                print(prefix + "└─ " + child)
                new_prefix = prefix + "   "
            else:
                print(prefix + "├─ " + child)
                new_prefix = prefix + "│  "
            print_subtree(node[child], new_prefix)

    # Print the root
    print_subtree(root)


def wrap_line(line: str, length: int, formatter: Callable) -> str: ...
