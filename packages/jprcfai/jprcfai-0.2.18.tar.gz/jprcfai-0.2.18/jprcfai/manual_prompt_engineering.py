import os
import subprocess
import sys
import tempfile
import time
import shutil
from typing import Optional, Callable
from .core import ask_gemini


def iterative_chat(initial_prompt: str = "", reasoning_effort: str = "pro") -> str:
    current_prompt = initial_prompt
    while True:
        current_prompt = edit_prompt_interactively(current_prompt)
        answer = ask_gemini(current_prompt, reasoning_effort)
        if (
            current_prompt.startswith("--> User:\n")
            and "--> You (AI agent):" in current_prompt
        ):
            current_prompt = "\n".join(
                [current_prompt, "----\n\nYou (AI agent):\n", answer]
            )
        else:
            current_prompt = "\n".join(
                [
                    "--> User:\n",
                    current_prompt,
                    "\n\n--> You (AI agent):\n",
                    answer,
                    "\n\n--> User:\n",
                ]
            )


def edit_prompt_interactively(initial_prompt: str) -> str:
    """
    Opens a temporary file containing the initial_prompt in VS Code for interactive editing.
    Waits until the prompt is updated by the user and returns the modified prompt.

    This implementation is OS independent in that it uses shutil.which to locate the VS Code
    command ('code') regardless of the operating system. If VS Code is not available in the PATH,
    the function will exit with an error message.
    """
    vs_code_path = shutil.which("code")
    if not vs_code_path:
        print(
            "Failed to open VS Code. 'code' command not found in PATH. Please install VS Code and add 'code' to your PATH."
        )
        sys.exit(1)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".txt", encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(initial_prompt)
            tmp_filepath = tmp_file.name

        print(
            f"\nInteractive mode enabled. Opening prompt file at {tmp_filepath} in VS Code...\n"
        )
        subprocess.Popen([vs_code_path, tmp_filepath])
    except Exception as e:
        print(
            f"Failed to open VS Code. Ensure 'code' is installed and in your PATH. Error: {e}"
        )
        sys.exit(1)

    print("Waiting for you to modify the prompt file and save your changes...")
    original_prompt_content = initial_prompt.strip()
    updated_prompt = original_prompt_content
    try:
        while updated_prompt == original_prompt_content or updated_prompt == "":
            time.sleep(1)
            with open(tmp_filepath, "r", encoding="utf-8") as f:
                updated_prompt = f.read().strip()
    except KeyboardInterrupt:
        print("\nEditing interrupted by user. Exiting.")
        sys.exit(1)

    try:
        os.unlink(tmp_filepath)
    except Exception as e:
        print(f"Warning: Could not delete temporary file {tmp_filepath}: {e}")

    print("Detected updated prompt. Proceeding with the modified prompt.\n")
    return updated_prompt


def get_user_prompt(
    interactive: bool,
    prompt_query: Optional[str],
    prompt_template_content: str,
    input_message: str,
    build_prompt: Optional[Callable[[str], str]] = None,
) -> str:
    """
    Generate the user prompt based on whether interactive mode is enabled.

    Args:
        interactive (bool): Flag indicating if interactive mode is enabled.
        prompt_query (Optional[str]): The prompt query provided by the user (can be None).
        prompt_template_content (str): The default prompt content if no query is provided.
        input_message (str): The message displayed when asking for input in non-interactive mode.
        build_prompt (Optional[Callable[[str], str]]): A function to transform the prompt query.
            If None, no transformation is applied.

    Returns:
        str: The final user prompt.
    """
    if not interactive:
        # Non-interactive mode: use provided prompt_query or ask for input.
        prompt_input = prompt_query or input(input_message).strip()
        user_prompt = (
            build_prompt(prompt_template_content, prompt_input)
            if build_prompt is not None
            else prompt_input
        )
    else:
        # Interactive mode:
        if prompt_query is not None:
            user_prompt = (
                build_prompt(prompt_template_content, prompt_query)
                if build_prompt is not None
                else prompt_query
            )
        else:
            user_prompt = prompt_template_content
        # Allow the user to edit the prompt interactively.
        user_prompt = edit_prompt_interactively(user_prompt)

    return user_prompt
