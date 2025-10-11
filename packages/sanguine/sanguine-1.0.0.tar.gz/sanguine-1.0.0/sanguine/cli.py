import argparse
import os
import subprocess
import sys
from functools import reduce
from typing import Optional

import sanguine.constants as c
import sanguine.git as git
import sanguine.meta as meta
from sanguine.db import db
from sanguine.db.fts import CodeEntity, type_to_id
from sanguine.install_uninstall import install, uninstall
from sanguine.parser import extract_symbols
from sanguine.utils import ext_to_lang, is_repo
from huepy import lightred, lightgreen

db.connect()
db.create_tables([CodeEntity])


def process_commit(commit_id: Optional[str] = None):
    if not is_repo():
        print(lightred("not a git repo"), file=sys.stderr)
        return

    try:
        file_to_diff = git.commit_diff(commit_id or git.last_commit())
    except subprocess.CalledProcessError:
        print(lightred("probably passed an invalid commit id"), file=sys.stderr)
        return

    for idx, (file, (added_lines, removed_lines)) in enumerate(file_to_diff.items()):
        ext = os.path.splitext(file)[1]
        if ext not in ext_to_lang:
            continue

        file_path = os.path.abspath(file)
        lang = ext_to_lang[ext]
        added_symbols = extract_symbols(added_lines, lang)
        removed_symbols = extract_symbols(removed_lines, lang)

        with db.atomic():
            for entity_type, field_name in [
                (c.ENTITY_FUNCTION, c.FLD_FUNCTIONS),
                (c.ENTITY_CLASS, c.FLD_CLASSES),
            ]:
                for symbol in added_symbols[field_name]:
                    CodeEntity.create(
                        file=file_path,
                        type=type_to_id[entity_type],
                        name=symbol[c.FLD_NAME],
                    )

                for symbol in removed_symbols[field_name]:
                    CodeEntity.delete().where(
                        (CodeEntity.file == file_path)
                        & (CodeEntity.type == type_to_id[entity_type])
                        & (CodeEntity.name == symbol[c.FLD_NAME])
                    )

        prog = (idx + 1) / len(file_to_diff)
        filled = int(prog * 80)
        print(
            lightgreen(f"[{meta.name}] [{'=' * filled}{' ' * (80 - filled)}]"),
            end="\r",
            file=sys.stderr,
        )

    print(lightgreen(f"[{meta.name}] [{'=' * 80}]\n"), file=sys.stderr)


def search(text: str, path: Optional[str] = None, type: Optional[str] = None):
    conditions = [CodeEntity.name.contains(text)]
    if path is not None:
        conditions.append(CodeEntity.file.startswith(path))
    if type is not None:
        conditions.append(CodeEntity.type == type_to_id[type])

    conditions = reduce(lambda x, y: x & y, conditions)
    objects = CodeEntity.select().where(conditions)
    for o in objects:
        print(f"{o.file} -> {o.name}({o.type})")


def main():
    parser = argparse.ArgumentParser(
        prog=meta.name,
        description="Pre-commit code analysis and indexing tool",
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog, max_help_position=25, width=120
        ),
        usage=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    subparsers.add_parser("install", help="Install pre-commit hooks")
    subparsers.add_parser("uninstall", help="Uninstall pre-commit hooks")

    index_parser = subparsers.add_parser(
        "index", help="Process and index commit changes"
    )
    index_parser.add_argument(
        "--commit-id",
        "-c",
        type=str,
        default=None,
        help="Specific commit ID to process (defaults to last commit)",
    )

    search_parser = subparsers.add_parser("search", help="Search for code entities")
    search_parser.add_argument(
        "text", type=str, help="Text to search for in code entity names"
    )
    search_parser.add_argument(
        "--path",
        "-p",
        type=str,
        default=None,
        help="Filter results by file path prefix",
    )
    search_parser.add_argument(
        "--type",
        "-t",
        type=str,
        default=None,
        choices=["function", "class"],
        help="Filter results by entity type (function or class)",
    )

    args = parser.parse_args(sys.argv[1:] or ["-h"])

    if args.command == "install":
        install()
    elif args.command == "uninstall":
        uninstall()
    elif args.command == "index":
        process_commit(args.commit_id)
    elif args.command == "search":
        search(args.text, args.path, args.type)
    else:
        parser.print_help()
        sys.exit(1)
