import subprocess
import os
from typing import Optional, List, Tuple
from .core import unroll_prompt_from_file, ask_openai

__all__ = [
    "extract_commit_diff",
    "extract_changed_files_content",
    "exctract_diff_along_with_files",
    "reduce_review_input_content",
    "create_review_from_changes_input",
]


def extract_commit_diff(revision: str, directory: str = ".") -> Optional[str]:
    """
    Extracts and returns the git diff between the given revision and HEAD,
    executed in the specified directory (defaults to ".").
    If an error occurs, the exception is raised.
    """
    commit_diff = subprocess.check_output(
        ["git", "diff", "-U50", revision, "HEAD"],
        stderr=subprocess.STDOUT,
        cwd=directory,
    ).decode("utf-8", errors="ignore")
    return commit_diff


def extract_changed_files_content(
    revision: str, directory: str = "."
) -> Tuple[List[str], str]:
    """
    Extracts the list of changed files (from git diff --name-only) between the given revision and HEAD,
    executed in the specified directory.
    For each changed file that exists in that directory and is smaller than 20kB, reads its full content and
    formats it with a header and separator.
    Returns a tuple: (changed_files_list, aggregated_files_content).
    If an error occurs while retrieving the file list, returns ([], "").
    """
    try:
        changed_files_output = (
            subprocess.check_output(
                ["git", "diff", "--name-only", revision, "HEAD"],
                stderr=subprocess.STDOUT,
                cwd=directory,
            )
            .decode("utf-8")
            .strip()
        )
        changed_files: List[str] = (
            changed_files_output.split("\n") if changed_files_output else []
        )
    except subprocess.CalledProcessError as e:
        print(
            "Error retrieving changed files between",
            revision,
            "and HEAD in directory",
            directory,
            ":\n",
            e.output.decode(),
        )
        return [], ""

    files_content = ""
    for cf in changed_files:
        cf = cf.strip()
        # Build the full file path relative to the directory
        file_path = os.path.join(directory, cf)
        if cf and os.path.isfile(file_path):
            try:
                # Check that the file is smaller than 20kB (20 * 1024 bytes)
                if os.path.getsize(file_path) < 20 * 1024:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_content = f.read()
                    files_content += f"\n# File: {cf}\n{file_content}\n\n---\n"
                else:
                    # Skip files that are 20kB or larger
                    continue
            except Exception as err:
                print(f"Error reading file {cf}: {err}")
    return changed_files, files_content


def exctract_diff_along_with_files(revision: str, directory: str = ".") -> str:
    """
    Combines the commit diff and changed file contents for the given revision,
    executed in the specified directory.
    Returns a formatted string with both the diff and file contents.
    """
    commit_diff = extract_commit_diff(revision, directory)
    if commit_diff is None:
        return "Error retrieving commit diff."
    changed_files, files_content = extract_changed_files_content(revision, directory)

    return (
        "1. Commit Diff:\n"
        + commit_diff.strip()
        + "\n\n2. New File Contents:\n"
        + files_content.strip()
    )


def reduce_review_input_content(
    input_content: str, reasoning_effort: str = "codex-medium"
) -> str:
    user_prompt = unroll_prompt_from_file("ReduceReviewInfo.txt")
    user_prompt = user_prompt.replace(
        "[CODE_DIFFS_CONCATENATED_WITH_FILE_CONTENTS]", input_content
    )

    reduced_input_content = ask_openai(user_prompt, reasoning_effort)

    return reduced_input_content


def create_review_from_changes_input(
    input_content: str, reasoning_effort: str = "codex-medium"
) -> str:
    user_prompt = unroll_prompt_from_file("ReviewCode.txt")
    user_prompt = user_prompt.replace("[APPLIED_CHANGES]", input_content)

    review_message = ask_openai(user_prompt, reasoning_effort)

    return review_message
