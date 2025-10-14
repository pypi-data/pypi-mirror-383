#!/usr/bin/env python3
from .core import ask_openai, unroll_prompt_from_file
from .code_review_utils import extract_commit_diff
from .manual_prompt_engineering import edit_prompt_interactively
from .logger_config import logger, reevaluate_logger_configuration

import subprocess
import tempfile
import os
import shutil
import shlex
import sys
from typing import Tuple, Dict, Optional, List


def use_tree_command(directory: str) -> str:
    """
    Build a tree-like listing of the contents of a directory and return the output.
    This function prints exactly what the linux command "tree" prints, but ignores the .git directory.

    Args:
        directory (str): The directory to list.
    Returns:
        str: The tree listing as a string.
    """
    logger.info("use_tree_command: starting with directory: %s", directory)
    from typing import List

    def tree(dir_path: str, prefix: str = "") -> List[str]:
        entries: List[str] = sorted(
            entry for entry in os.listdir(dir_path) if entry != ".git"
        )
        lines: List[str] = []
        for index, entry in enumerate(entries):
            path: str = os.path.join(dir_path, entry)
            if index == len(entries) - 1:
                connector: str = "└── "
                new_prefix: str = prefix + "    "
            else:
                connector: str = "├── "
                new_prefix: str = prefix + "│   "
            lines.append(prefix + connector + entry)
            if os.path.isdir(path):
                lines.extend(tree(path, new_prefix))
        return lines

    root_name: str = os.path.basename(os.path.abspath(directory))
    output_lines: List[str] = [root_name]
    output_lines.extend(tree(directory))

    total_dirs: int = 0
    total_files: int = 0
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d != ".git"]
        total_dirs += len(dirs)
        total_files += len(files)
    output_lines.append("")
    output_lines.append(f"{total_dirs} directories, {total_files} files")
    logger.info(
        "use_tree_command: computed totals: %d directories, %d files",
        total_dirs,
        total_files,
    )
    logger.info(
        "use_tree_command: returning tree structure with %d lines", len(output_lines)
    )
    return "\n".join(output_lines)


def execute_python_command(python_code: str, directory: str) -> str:
    """
    Execute provided Python code in a temporary script file.
    The function attempts to use a Python 3 interpreter if available.
    On Windows, it first checks for 'python3' and, if not found, falls back to
    the default Python interpreter (sys.executable).

    Args:
        python_code (str): The Python code to execute.
        directory (str): The working directory for execution.

    Returns:
        str: The standard output of the executed command.
    """
    logger.info(
        "execute_python_command: starting execution in directory: %s", directory
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
        temp_file.write(python_code)
        temp_file.flush()
        temp_filename: str = temp_file.name
    logger.info("execute_python_command: temporary script created at %s", temp_filename)

    try:
        if os.name != "nt":
            os.chmod(temp_filename, 0o755)
            logger.info(
                "execute_python_command: set execute permissions for %s", temp_filename
            )

        if os.name == "nt":
            python_path: Optional[str] = shutil.which("python3")
            if python_path:
                command: List[str] = [python_path, temp_filename]
                logger.info(
                    "execute_python_command: Windows - using python3 at %s", python_path
                )
                result = subprocess.run(
                    command, cwd=directory, capture_output=True, text=True
                )
            else:
                command = [sys.executable, temp_filename]
                logger.info(
                    "execute_python_command: Windows - using sys.executable: %s",
                    sys.executable,
                )
                result = subprocess.run(
                    command, cwd=directory, capture_output=True, text=True
                )
        else:
            python_path = shutil.which("python3")
            if python_path:
                command = [python_path, temp_filename]
                logger.info(
                    "execute_python_command: POSIX - using python3 at %s", python_path
                )
            else:
                command = [sys.executable, temp_filename]
                logger.info(
                    "execute_python_command: POSIX - using sys.executable: %s",
                    sys.executable,
                )
            logger.info("execute_python_command: running command: %s", command)
            result = subprocess.run(
                command, cwd=directory, capture_output=True, text=True
            )
        logger.info(
            "execute_python_command: subprocess finished with exit code %d",
            result.returncode,
        )
    finally:
        os.remove(temp_filename)
        logger.info(
            "execute_python_command: temporary script %s removed", temp_filename
        )

    logger.info(
        "execute_python_command: returning output of length %d", len(result.stdout)
    )
    if result.stderr:
        return (
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"Exit code: {result.returncode}"
        )
    return result.stdout


def execute_bash_command(bash_code: str, directory: str) -> str:
    """
    Execute provided bash code in a temporary script file.
    On POSIX systems, this uses bash.
    On Windows, it first checks for bash availability (e.g. Git Bash, WSL)
    and if not found falls back to the default shell.

    Args:
        bash_code (str): The bash code to execute.
        directory (str): The working directory for execution.
    Returns:
        str: The standard output of the executed command.
    """
    logger.info("execute_bash_command: starting execution in directory: %s", directory)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as temp_file:
        temp_file.write(bash_code)
        temp_file.flush()
        temp_filename: str = temp_file.name
    logger.info(
        "execute_bash_command: temporary bash script created at %s", temp_filename
    )

    try:
        if os.name != "nt":
            os.chmod(temp_filename, 0o755)
            logger.info(
                "execute_bash_command: set execute permissions for %s", temp_filename
            )

        if os.name == "nt":
            bash_path: Optional[str] = shutil.which("bash")
            if bash_path:
                command: List[str] = [bash_path, temp_filename]
                logger.info(
                    "execute_bash_command: Windows - using bash at %s with command: %s",
                    bash_path,
                    command,
                )
                result = subprocess.run(
                    command, cwd=directory, capture_output=True, text=True
                )
            else:
                logger.info(
                    "execute_bash_command: Windows - no bash found, using default shell for %s",
                    temp_filename,
                )
                result = subprocess.run(
                    temp_filename,
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    shell=True,
                )
        else:
            logger.info("execute_bash_command: POSIX - executing with bash")
            result = subprocess.run(
                ["bash", temp_filename], cwd=directory, capture_output=True, text=True
            )
        logger.info(
            "execute_bash_command: subprocess finished with exit code %d",
            result.returncode,
        )
    finally:
        os.remove(temp_filename)
        logger.info(
            "execute_bash_command: temporary bash script %s removed", temp_filename
        )

    logger.info(
        "execute_bash_command: returning output of length %d", len(result.stdout)
    )
    return result.stdout


def refactor_code(replace_map: Dict[str, str], directory: str) -> Tuple[str, str]:
    """
    Refactor code based on a replacement map.

    Args:
        replace_map (Dict[str, str]): A dictionary with keys and corresponding replacement values.
        directory (str): The working directory for execution.
    Returns:
        Tuple[str, str]: A tuple containing the bash script code and its command output.
    """
    logger.info("refactor_code: starting with replace_map: %s", replace_map)
    refactor_prompt: str = unroll_prompt_from_file("Refactor.txt", unroll=True)
    logger.info("refactor_code: loaded prompt template from Refactor.txt")

    for key, value in replace_map.items():
        refactor_prompt = refactor_prompt.replace(f"[{key}]", value)
    logger.info(
        "refactor_code: filled prompt (first 100 chars): %s", refactor_prompt[:100]
    )

    logger.info("refactor_code: sending prompt to OpenAI")
    bash_file_code: str = ask_openai(refactor_prompt, "codex-medium")
    logger.info(
        "refactor_code: received bash code from OpenAI (first 100 chars): %s",
        bash_file_code[:100],
    )

    logger.info("refactor_code: executing bash command in directory: %s", directory)
    command_output: str = execute_bash_command(bash_file_code, directory)
    logger.info(
        "refactor_code: received command output (first 100 chars): %s",
        command_output[:100],
    )
    logger.info("refactor_code: finished refactoring step")
    return bash_file_code, command_output


def retrieve_information(
    replace_map: Dict[str, str], directory: str
) -> Tuple[str, str]:
    """
    Retrieve information based on a replacement map.

    Args:
        replace_map (Dict[str, str]): A dictionary with keys and corresponding replacement values.
        directory (str): The working directory for execution.
    Returns:
        Tuple[str, str]: A tuple containing the bash script code and its command output.
    """
    logger.info("retrieve_information: starting with replace_map: %s", replace_map)
    refactor_prompt: str = unroll_prompt_from_file("RetrieveInfomaton.txt", unroll=True)
    logger.info(
        "retrieve_information: loaded prompt template from RetrieveInfomaton.txt"
    )

    for key, value in replace_map.items():
        refactor_prompt = refactor_prompt.replace(f"[{key}]", value)
    logger.info(
        "retrieve_information: filled prompt (first 100 chars): %s",
        refactor_prompt[:100],
    )

    logger.info("retrieve_information: sending prompt to OpenAI")
    bash_file_code: str = ask_openai(refactor_prompt, "codex-medium")
    logger.info(
        "retrieve_information: received bash code from OpenAI (first 100 chars): %s",
        bash_file_code[:100],
    )

    logger.info(
        "retrieve_information: executing bash command in directory: %s", directory
    )
    command_output: str = execute_bash_command(bash_file_code, directory)
    logger.info(
        "retrieve_information: received command output (first 100 chars): %s",
        command_output[:100],
    )
    return bash_file_code, command_output


def summarize_work_done(replace_map: Dict[str, str], directory: str) -> str:
    """
    Summarize the work done based on a replacement map.

    Args:
        replace_map (Dict[str, str]): A dictionary with keys and corresponding replacement values.
        directory (str): The working directory for execution.
    Returns:
        str: The summary of the work done.
    """
    logger.info("summarize_work_done: starting with replace_map: %s", replace_map)
    summary_prompt: str = unroll_prompt_from_file("RefactorSummary.txt", unroll=True)
    logger.info("summarize_work_done: loaded prompt template from RefactorSummary.txt")

    for key, value in replace_map.items():
        summary_prompt = summary_prompt.replace(f"[{key}]", value)
    logger.info(
        "summarize_work_done: filled summary prompt (first 100 chars): %s",
        summary_prompt[:100],
    )

    logger.info("summarize_work_done: sending summary prompt to OpenAI")
    summary: str = ask_openai(summary_prompt, "codex-medium")
    logger.info(
        "summarize_work_done: received summary from OpenAI (first 100 chars): %s",
        summary[:100],
    )
    return summary


def checkpoint_next_action(replace_map: Dict[str, str], directory: str) -> str:
    """
    Determine the next action to take based on the checkpoint prompt.

    Args:
        replace_map (Dict[str, str]): A dictionary with keys and corresponding replacement values.
        directory (str): The working directory for execution.
    Returns:
        str: The result from the checkpoint next action prompt.
    """
    logger.info("checkpoint_next_action: starting with replace_map: %s", replace_map)
    checkpoint_prompt: str = unroll_prompt_from_file(
        "CheckpointerRedirecter.txt", unroll=True
    )
    logger.info(
        "checkpoint_next_action: loaded prompt template from CheckpointerRedirecter.txt"
    )

    for key, value in replace_map.items():
        checkpoint_prompt = checkpoint_prompt.replace(f"[{key}]", value)
    logger.info(
        "checkpoint_next_action: filled checkpoint prompt (first 100 chars): %s",
        checkpoint_prompt[:100],
    )

    logger.info("checkpoint_next_action: sending checkpoint prompt to OpenAI")
    result: str = ask_openai(checkpoint_prompt, "codex-medium")
    logger.info("checkpoint_next_action: received response from OpenAI: %s", result)
    return result


def code_test_command(test_command: str, directory: str) -> str:
    """
    Execute a test command in the specified directory.
    Uses OS detection to run the command appropriately.

    Args:
        test_command (str): The command to run.
        directory (str): The working directory for execution.
    Returns:
        str: The output from executing the test command.
    """
    logger.info(
        "code_test_command: executing test command: '%s' in directory: %s",
        test_command,
        directory,
    )
    try:
        if os.name == "nt":
            result = subprocess.run(
                test_command, cwd=directory, capture_output=True, text=True, shell=True
            )
        else:
            args: List[str] = shlex.split(test_command)
            result = subprocess.run(args, cwd=directory, capture_output=True, text=True)
        logger.info(
            "code_test_command: subprocess finished with exit code %d",
            result.returncode,
        )
    except Exception as e:
        logger.error("code_test_command: error executing test command: %s", e)
        return f"An error occurred while executing the test command: {e}"

    if result.stdout or result.stderr:
        return (
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"Exit code: {result.returncode}"
        )
    else:
        return f"Program exited with code {result.returncode}"


def execute_major_coding_task(
    task_instruction: str, directory: str, test_command: str, max_retries: int = 15
) -> Optional[Dict[str, str]]:
    """
    Execute a major coding task.

    Args:
        task_instruction (str): The task instruction.
        directory (str): The directory where the task will be executed.
        test_command (str): The command used to test the code.
        max_retries (int, optional): Maximum number of retries allowed (default is 15).
    Returns:
        Optional[Dict[str, str]]: The replacement map with updated values if finished,
                                  or None if the task could not be completed.
    """
    # Re-evaluate logging configuration for this function
    reevaluate_logger_configuration()
    logger.info(
        "execute_major_coding_task: starting with task_instruction: %s, directory: %s, test_command: %s",
        task_instruction,
        directory,
        test_command,
    )
    if not os.path.exists(os.path.join(directory, ".git")):
        logger.info(
            "execute_major_coding_task: No .git directory found, initializing new git repository"
        )
        subprocess.run(["git", "init"], cwd=directory, check=True)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "Initial commit"],
            cwd=directory,
            check=True,
        )
    try:
        subprocess.run(
            ["git", "checkout", "-b", "ai-refactor"], cwd=directory, check=True
        )
        logger.info(
            "execute_major_coding_task: created and switched to branch 'ai-refactor'"
        )
    except subprocess.CalledProcessError:
        subprocess.run(["git", "checkout", "ai-refactor"], cwd=directory, check=True)
        logger.info(
            "execute_major_coding_task: switched to existing branch 'ai-refactor'"
        )

    base_commit_hash = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=directory,
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    ).stdout.strip()
    logger.info(
        "execute_major_coding_task: captured base commit hash: %s", base_commit_hash
    )

    replace_map: Dict[str, str] = {
        "TASK_INSTRUCTION_PLACEHOLDER": task_instruction,
        "TREE_COMMAND_PLACEHOLDER": use_tree_command(directory),
        "EXTRACTED_INFORMATION_PLACEHOLDER": "",
        "WORK_DONE_PLACEHOLDER": "",
        "TEST_OUTPUT_COMMAND": "No command was executed to test the code",
        "TEST_COMMAND": test_command,
    }
    logger.info("execute_major_coding_task: initial replace_map constructed.")

    attempts: int = 0
    while attempts < max_retries:
        logger.info(
            "execute_major_coding_task: attempt %d of %d", attempts + 1, max_retries
        )
        response: str = checkpoint_next_action(replace_map, directory)
        logger.info("execute_major_coding_task: checkpoint response: %s", response)

        if response == "refactor":
            logger.info("execute_major_coding_task: response indicated 'refactor'")
            bash_file_code, command_output = refactor_code(replace_map, directory)
            subprocess.run(["git", "add", "."], cwd=directory, check=True)
            subprocess.run(
                ["git", "commit", "-m", "refactor"], cwd=directory, check=True
            )
            logger.info(
                "execute_major_coding_task: performed git add and commit after refactoring"
            )
            full_diff = extract_commit_diff(base_commit_hash, directory)
            replace_map["WORK_DONE_PLACEHOLDER"] = full_diff
            logger.info("execute_major_coding_task: captured diff from base commit")

            replace_map["BASH_SCRIPT_PLACEHOLDER"] = bash_file_code

            replace_map["TEST_OUTPUT_COMMAND"] = code_test_command(
                test_command, directory
            )
            logger.info("execute_major_coding_task: updated test command output")
            replace_map["TREE_COMMAND_PLACEHOLDER"] = use_tree_command(directory)
            replace_map["EXTRACTED_INFORMATION_PLACEHOLDER"] = ""
        elif response == "finish":
            logger.info(
                "execute_major_coding_task: response indicated 'finish'. Ending task."
            )
            return replace_map
        elif response == "retrieve":
            logger.info("execute_major_coding_task: response indicated 'retrieve'")
            bash_file_code, command_output = retrieve_information(
                replace_map, directory
            )
            replace_map["EXTRACTED_INFORMATION_PLACEHOLDER"] = command_output
            logger.info("execute_major_coding_task: updated extracted information")
        attempts += 1

    logger.info("execute_major_coding_task: Maximum retries reached. Exiting loop.")
    print("Maximum retries reached in execute_major_coding_task. Exiting loop.")
    return None


def apply_changes_to_code(
    code: str,
    changes: str,
    reasoning_effort: str,
    interactive: bool,
) -> str:
    """
    Apply requested modifications to a code file.

    This function retrieves a prompt template for single file code modifications,
    inserts the provided code content and requested changes, and (if enabled)
    allows for interactive editing of the prompt before sending it to OpenAI.

    Args:
        code (str): The current content of the code.
        changes (str): The changes to be applied to the code.
        reasoning_effort (str): The reasoning effort level used for requesting changes.
        interactive (bool): Whether to allow interactive editing of the prompt.

    Returns:
        str: The updated code with the applied modifications.
    """
    logger.info(
        "apply_changes_to_code: starting with code of length %d, changes of length %d, interactive=%s",
        len(code),
        len(changes),
        interactive,
    )
    prompt_template: str = unroll_prompt_from_file("SingleFileCodeModifications.txt")
    logger.info(
        "apply_changes_to_code: loaded prompt template from SingleFileCodeModifications.txt"
    )
    # The following replace chain inserts the current code and the requested changes.
    prompt_filled: str = prompt_template.replace("[FILE_CONTENT]", code).replace(
        "[REQUEST_CHANGES]", changes
    )
    logger.info(
        "apply_changes_to_code: filled prompt (first 100 chars): %s",
        prompt_filled[:100],
    )
    if interactive:
        logger.info(
            "apply_changes_to_code: interactive mode enabled, invoking edit_prompt_interactively"
        )
        prompt_filled = edit_prompt_interactively(prompt_filled)
        logger.info(
            "apply_changes_to_code: prompt after interactive editing (first 100 chars): %s",
            prompt_filled[:100],
        )

    logger.info(
        "apply_changes_to_code: sending prompt to OpenAI with reasoning effort: %s",
        reasoning_effort,
    )
    updated_code: str = ask_openai(prompt_filled, reasoning_effort)
    logger.info(
        "apply_changes_to_code: received updated code from OpenAI (first 100 chars): %s",
        updated_code[:100],
    )

    trimmed_code = updated_code.strip()
    if trimmed_code.startswith("```") and trimmed_code.endswith("```"):
        lines = trimmed_code.split("\n")
        if len(lines) > 2:
            updated_code = "\n".join(lines[1:-1])
        else:
            # Handle case where there's nothing between the fences
            updated_code = ""

    return updated_code
