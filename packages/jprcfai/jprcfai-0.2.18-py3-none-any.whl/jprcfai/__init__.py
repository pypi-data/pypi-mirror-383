# jprcfai/__init__.py

# Optional: automatically set the assistants directory so that unroll_prompt_from_file works.
import os
from importlib.resources import files


def resource_filename(package, resource):
    return str(files(package).joinpath(resource))


# Set the ASSISTANTS_DIR environment variable to point to the package's assistants folder.
assistants_dir = resource_filename(__name__, "assistants")
os.environ.setdefault("ASSISTANTS_DIR", assistants_dir)

# Import functions from core.py to expose them at the package level.
from .core import (
    ask_openai,
    ask_gemini,
    unroll_prompt_from_file,
    get_repo_name,
    unroll_prompt_from_git,
    unroll_prompt,
    execute_local_script_with_browser,
)

from .complex_coding_tasks import (
    execute_major_coding_task,
    apply_changes_to_code,
    execute_python_command,
    execute_bash_command,
)

from .simple_coding_tasks import (
    fix_single_code_file,
    ERROR_AFTER_TIMER,
    OK_AFTER_TIMER,
    WAIT_UNTIL_FINISH,
)

from . import code_review_utils

from .manual_prompt_engineering import (
    edit_prompt_interactively,
    get_user_prompt,
    iterative_chat,
)
