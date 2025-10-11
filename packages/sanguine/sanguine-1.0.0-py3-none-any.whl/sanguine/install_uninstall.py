import os
import shutil
import stat
import textwrap

import sanguine.meta as meta
from sanguine.utils import is_repo
from huepy import lightred, lightgreen


def install():
    if not is_repo():
        print(lightred("not a git repository"))
        return

    hooks_dir = ".git/hooks"
    hook_file = os.path.join(hooks_dir, "post-commit")
    os.makedirs(hooks_dir, exist_ok=True)
    py_exe = shutil.which("python").replace("\\", "/")

    script = textwrap.dedent(
        f"""\
        #!/bin/sh
        export FORCE_COLOR=1
        export TERM=xterm-256color
        
        PYTHON="{py_exe}"
        PREFIX=""

        if [ -x "$PYTHON" ]; then
            exec "$PYTHON" -m{meta.name} index
        elif command -v {meta.name} > /dev/null; then
            exec {meta.name} index
        else
            echo "{meta.name} not found"
            echo "what ra sudeep, too much mistake you're making bro!?"
            exit 1
        fi
        """
    )

    with open(hook_file, "w") as f:
        f.write(script)
    os.chmod(hook_file, os.stat(hook_file).st_mode | stat.S_IXUSR)
    print(lightgreen(f"{meta.name} has been installed!"))


def uninstall():
    hook_file = ".git/hooks/post-commit"
    if os.path.exists(hook_file):
        os.remove(hook_file)
    print(lightgreen(f"{meta.name} has been uninstalled!"))
