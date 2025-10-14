import ast
from pathlib import Path


class OutlinePrinter:
    def __init__(self, show_args=False, use_emoji=True):
        self.show_args = show_args
        self.use_emoji = use_emoji

    def _icon(self, kind):
        if not self.use_emoji:
            return ""
        return {
            "file": "📄 ",
            "class": "♾️  ",
            "func": "📦 ",
        }.get(kind, "")

    def print_outline(self, path: Path):
        if path.is_file() and path.suffix == ".py":
            print(f"{self._icon('file')}{path.name}")
            self._print_file_outline(path)
        elif path.is_dir():
            print(f"📁 {path}")
            for file in sorted(path.rglob("*.py")):
                rel = file.relative_to(path)
                print(f"\n{self._icon('file')}{rel}")
                self._print_file_outline(file)
        else:
            print(f"⚠️  Not a Python file or directory: {path}")

    def _print_file_outline(self, path: Path):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"    ⚠️  Failed to parse: {e}")
            return

        for node in tree.body:
            self._walk(node, prefix="")

    def _walk(self, node, prefix, is_last=False):
        connector = "└── " if is_last else "├── "
        if isinstance(node, ast.ClassDef):
            print(f"{prefix}{connector}{self._icon('class')}class {node.name}")
            for i, child in enumerate(node.body):
                self._walk(
                    child,
                    prefix + ("    " if is_last else "│   "),
                    i == len(node.body) - 1,
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            args = ""
            if self.show_args:
                args = "(" + ", ".join(a.arg for a in node.args.args) + ")"
            print(f"{prefix}{connector}{self._icon('func')}{kind} {node.name}{args}")
