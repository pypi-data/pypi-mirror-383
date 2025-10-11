import json
import os

core_dir = os.path.dirname(__file__)

prog_lang_schema = json.load(
    open(os.path.join(core_dir, "assets", "prog_langs_schema.json"))
)
ext_to_lang = json.load(
    open(os.path.join(core_dir, "assets", "ext_to_lang.json"))
)


def is_repo():
    return os.path.exists(".git")
