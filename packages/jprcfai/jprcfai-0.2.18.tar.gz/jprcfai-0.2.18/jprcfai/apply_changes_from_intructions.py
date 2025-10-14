#!/usr/bin/env python3
import os
import subprocess
from typing import Optional, List
import uuid
import concurrent.futures
import logging
import sys
from .core import ask_gemini
from .code_review_utils import extract_commit_diff

logger = logging.getLogger(__name__)


# Function to check if the text is wrapped in code fences
# We are only interested when the last line is a closing code fence and is after a '\n' (not any other new line character)
def is_wrapped_in_code_fences(text: str) -> bool:
    return text.startswith("```") and text.rstrip().endswith("\n```")


# --- Configuration ---
OUTPUT_FILE = "candidate_list.txt"  # Output file for the suggestion patch
PATCH_PROMPT_FILE = (
    ".github/scripts/CreatePatchFile.txt"  # Name of the prompt template file
)
CANDIDATE_LIST_PROMPT_FILE = (
    "SelectCandidateFiles.txt"  # Name of the prompt template file
)
FILE_MODIFICATION_PROMPT_FILE = "SingleFileCodeModifications.txt"
REVIEW_FILE = "review.txt"  # Input file from the review comment
APPLIED_CHANGES_PLACEHOLDER = (
    "[APPLIED_CHANGES]"  # Placeholder in the prompt file for the diff
)
REVIEWED_CHANGES_PLACEHOLDER = (
    "[REVIEW]"  # Placeholder in the prompt file for the review
)
FILE_LIST_PLACEHOLDER = (
    "[FILE_LIST]"  # Placeholder in the prompt file for the file list
)
FILE_NAME_PLACEHOLDER = (
    "[FILE_NAME]"  # Placeholder in the prompt file for the file name
)
FILE_CONTENT_PLACEHOLDER = (
    "[FILE_CONTENT]"  # Placeholder in the prompt file for the file content
)
REASONING_EFFORT = "pro"  # desired OpenAI effort/cost
# --- /Configuration ---


def extract_candidate_files(
    base_revision: str, head_revision: str, directory: str = "."
) -> List[str]:
    """
    Extracts the list of changed files (from git diff --name-only) between the given base and head revisions,
    executed in the specified directory.
    Filters the list to include only files that currently exist in the directory.
    Returns a list of existing changed files.
    If an error occurs while retrieving the file list, returns an empty list.
    """
    try:
        changed_files_output = (
            subprocess.check_output(
                ["git", "diff", "--name-only", base_revision, head_revision],
                stderr=subprocess.STDOUT,
                cwd=directory,
            )
            .decode("utf-8")
            .strip()
        )
        # Split the output into a list of file paths
        changed_files: List[str] = (
            changed_files_output.split("\n") if changed_files_output else []
        )
    except subprocess.CalledProcessError as e:
        logger.exception(
            f"Error retrieving changed files between {base_revision} and {head_revision} in directory {directory}:\n{e.output.decode()}"
        )
        return []

    # Filter the list to include only files that exist at the moment (i.e. not deleted)
    # Exclude empty files from processing
    # .github/workflows is protected and should not be modified
    existing_files = [
        f
        for f in changed_files
        if os.path.exists(os.path.join(directory, f))
        and os.path.getsize(os.path.join(directory, f)) > 0
        and not f.startswith(".github/workflows/")
    ]
    logger.info(f"Existing files: {existing_files}")

    return existing_files


def request_candidate_files_filtering(
    diff_content: str, review: str, file_list: List[str], reasoning_effort: str = "pro"
) -> Optional[str]:
    """
    Reads the prompt template, injects the diff and the file list to get the list of candidate files.
    """
    if not diff_content.strip() or not file_list:
        return "no candidates"

    try:
        # This path is now relative to the repository root, where the action executes
        with open(CANDIDATE_LIST_PROMPT_FILE, "r", encoding="utf-8") as prompt_file:
            user_prompt_template = prompt_file.read()
        logger.info(f"Read prompt template from {CANDIDATE_LIST_PROMPT_FILE}")
    except FileNotFoundError as e:
        logger.exception(
            f"Error: Required prompt file '{CANDIDATE_LIST_PROMPT_FILE}' is missing."
        )
        raise
    except IOError as e:
        logger.exception(
            f"Error reading prompt file '{CANDIDATE_LIST_PROMPT_FILE}': {e}"
        )
        raise

    file_list_content = "\n".join(f"{file}" for file in file_list)

    # Generate a unique ID
    uid = uuid.uuid4().hex

    # Create unique placeholders with AI prefix
    applied_changes_placeholder = f"<<AI_PLACEHOLDER_APPLIED_CHANGES_{uid}>>"
    reviewed_changes_placeholder = f"<<AI_PLACEHOLDER_REVIEWED_CHANGES_{uid}>>"
    file_list_placeholder = f"<<AI_PLACEHOLDER_FILE_LIST_{uid}>>"

    # Step 1: Replace fixed placeholders with unique temporary ones
    temp_prompt = (
        user_prompt_template.replace(
            APPLIED_CHANGES_PLACEHOLDER, applied_changes_placeholder
        )
        .replace(REVIEWED_CHANGES_PLACEHOLDER, reviewed_changes_placeholder)
        .replace(FILE_LIST_PLACEHOLDER, file_list_placeholder)
    )

    # Step 2: Replace unique placeholders with actual content
    user_prompt = (
        temp_prompt.replace(applied_changes_placeholder, diff_content)
        .replace(reviewed_changes_placeholder, review)
        .replace(file_list_placeholder, file_list_content)
    )

    logger.info("Sending prompt to OpenAI for retrieving candidate files...")
    agent_response = ask_gemini(user_prompt, reasoning_effort)
    if agent_response is None:
        raise ValueError(
            "Error: No response received from OpenAI for candidate file filtering."
        )

    return agent_response


def create_patch_file_from_review(
    file_name: str, file_content: str, review: str, reasoning_effort: str = "pro"
) -> Optional[str]:
    """
    Reads the prompt template, injects the file_name, file_content, and review into the prompt,
    and retrieves the patch content from OpenAI.

    Args:
        file_name (str): The name of the file.
        file_content (str): The content of the file.
        review (str): The review message or diff information.
        reasoning_effort (str, optional): The reasoning effort level; default is "pro".

    Returns:
        Optional[str]: The generated patch content or an error message.
        Note: A response of "no patch" is considered valid and indicates that no modifications should be applied.
    """
    try:
        # This path is now relative to the repository root, where the action executes
        with open(PATCH_PROMPT_FILE, "r", encoding="utf-8") as prompt_file:
            user_prompt_template = prompt_file.read()
        logger.info(f"Read prompt template from {PATCH_PROMPT_FILE}")
    except FileNotFoundError:
        logger.exception(
            f"Error: Required prompt file '{PATCH_PROMPT_FILE}' is missing."
        )
        raise
    except IOError as e:
        logger.exception(f"Error reading prompt file '{PATCH_PROMPT_FILE}': {e}")
        raise

    # Generate unique placeholders
    uid = uuid.uuid4().hex

    # Create unique temporary placeholders with AI prefix
    review_placeholder = f"<<AI_PLACEHOLDER_REVIEWED_CHANGES_{uid}>>"
    file_name_placeholder = f"<<AI_PLACEHOLDER_FILE_NAME_{uid}>>"
    file_content_placeholder = f"<<AI_PLACEHOLDER_FILE_CONTENT_{uid}>>"

    # Step 1: Replace template placeholders with unique ones
    temp_prompt = (
        user_prompt_template.replace(REVIEWED_CHANGES_PLACEHOLDER, review_placeholder)
        .replace(FILE_NAME_PLACEHOLDER, file_name_placeholder)
        .replace(FILE_CONTENT_PLACEHOLDER, file_content_placeholder)
    )

    # Step 2: Inject actual content
    user_prompt = (
        temp_prompt.replace(review_placeholder, review)
        .replace(file_name_placeholder, file_name)
        .replace(file_content_placeholder, file_content)
    )

    logger.info("Sending prompt to OpenAI for review...")
    agent_response = ask_gemini(user_prompt, reasoning_effort)

    return agent_response


def validate_candidate_files(
    candidate_files: List[str], filtered_files_str: str
) -> List[str]:
    # Convert filtered string into list and strip whitespace
    filtered_files = (
        [f.strip() for f in filtered_files_str.strip().split("\n") if f.strip()]
        if filtered_files_str.strip().lower() != "no candidates"
        else []
    )

    # Check if every filtered file is in candidate files
    invalid_files = [f for f in filtered_files if f not in candidate_files]
    if invalid_files:
        raise ValueError(f"Filtered files contain invalid entries: {invalid_files}")

    return filtered_files


def apply_changes_to_file(
    content: str,
    changes: str,
    reasoning_effort: str = "pro",
) -> str:
    """
    Apply requested modifications to a file.

    This function retrieves a prompt template for single file content modifications,
    inserts the provided file content along with the requested changes.

    Args:
        content (str): The current content of the file.
        changes (str): The changes to be applied to the file.
        reasoning_effort (str): The reasoning effort level used for requesting changes.

    Returns:
        str: The updated code with the applied modifications.
    """
    with open(FILE_MODIFICATION_PROMPT_FILE, "r", encoding="utf-8") as prompt_file:
        prompt_template = prompt_file.read()

    # The following replace chain inserts the current code and the requested changes.
    # Step 1: Use temporary placeholders that are unlikely to appear in code/changes

    uid = uuid.uuid4().hex
    file_placeholder = f"<<AI_PLACEHOLDER_FILE_CONTENT_{uid}>>"
    changes_placeholder = f"<<AI_PLACEHOLDER_REQUEST_CHANGES_{uid}>>"

    # Step 1: Replace original markers with unique placeholders
    temp_prompt = prompt_template.replace("[FILE_CONTENT]", file_placeholder).replace(
        "[REQUEST_CHANGES]", changes_placeholder
    )

    # Step 2: Replace placeholders with actual content
    prompt_filled: str = temp_prompt.replace(file_placeholder, content).replace(
        changes_placeholder, changes
    )

    updated_code: str = ask_gemini(prompt_filled, reasoning_effort)

    return updated_code


def main():
    """
    Main function to orchestrate the code review process.
    """
    logger.info("Starting AI Code Review Action...")

    base_sha = os.getenv("BASE_SHA")
    head_sha = os.getenv("HEAD_SHA")

    try:
        # This path is now relative to the repository root, where the action executes
        with open(REVIEW_FILE, "r", encoding="utf-8") as prompt_file:
            ai_review = prompt_file.read()
        logger.info(f"Read prompt template from {REVIEW_FILE}")
    except FileNotFoundError:
        logger.exception(f"Error: Required prompt file '{REVIEW_FILE}' is missing.")
        sys.exit(1)
    except IOError as e:
        logger.exception(f"Error reading prompt file '{REVIEW_FILE}': {e}")
        sys.exit(1)

    diff = extract_commit_diff(base_sha, head_sha)

    files = extract_candidate_files(base_sha, head_sha)

    # Create the review using the diff
    filtered_files_str = request_candidate_files_filtering(diff, ai_review, files)

    filtered_files = validate_candidate_files(files, filtered_files_str)

    # Write the final patch/error message to the output file if it's not empty
    if not filtered_files:
        logger.info("No files to process. Nothing to write.")
        sys.exit(0)

    def process_file(file_name):
        """
        Process a single file:
        - Reads file content.
        - Generates a patch using the review response.
        - Applies the requested changes.
        - Writes the updated file back.
        """
        try:
            # Read the original file content
            with open(file_name, "r", encoding="utf-8") as code_file:
                original_file_content = code_file.read()

            # Create patch from review
            patch_content = create_patch_file_from_review(
                file_name,
                original_file_content,
                ai_review,  # assuming ai_review is defined in the outer scope
            )

            if patch_content is None:
                error_message = f"Error: Failed to get patch suggestions from OpenAI for file {file_name}."
                logger.error(error_message)
                raise ValueError(error_message)
            else:
                final_patch_content = patch_content
                logger.info(f"Patch content received from OpenAI for {file_name}.")

            # Get the requested changes from the patch
            requested_changes = final_patch_content.strip()

            if requested_changes.strip().lower() == "no patch":
                logger.info(f"No changes requested for {file_name}.")
                return

            # Apply the requested changes to the code
            modified_file_content = apply_changes_to_file(
                original_file_content,
                requested_changes,
                REASONING_EFFORT,
            )

            # If the file was not wrapped in code fences, reject the addition of code fences
            if not is_wrapped_in_code_fences(
                original_file_content
            ) and is_wrapped_in_code_fences(modified_file_content):
                # The first line may have additional characters in the first line after the triple backticks.
                # In this case the whole line is intentionally removed including the additional words like (e.g. "python", "markdown", etc.)
                modified_file_content = "\n".join(
                    modified_file_content.split("\n")[1:-1]
                )
            if not modified_file_content.endswith("\n"):
                modified_file_content += "\n"
            # Write the updated code back to the file
            with open(file_name, "w", encoding="utf-8") as code_file:
                code_file.write(modified_file_content)

            logger.info(f"Applied changes to {file_name} and saved.")

        except Exception as e:
            logger.exception(f"Error processing file {file_name}: {e}")
            raise

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_file = {
            executor.submit(process_file, file_name): file_name
            for file_name in filtered_files
        }

        errors = []
        for future in concurrent.futures.as_completed(future_to_file):
            file_name = future_to_file[future]
            try:
                future.result()
            except Exception as e:
                logger.exception(f"Exception occurred when processing {file_name}: {e}")
                errors.append(file_name)
        if errors:
            logger.error("Errors occurred while processing files: " + ", ".join(errors))
            sys.exit(1)

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered_files))

        logger.info(f"Writing file list to {OUTPUT_FILE}")
        logger.info("Content:")
        logger.info("\n".join(filtered_files))
        logger.info(f"Successfully wrote to {OUTPUT_FILE}")
    except IOError as e:
        logger.exception(f"Error writing output file '{OUTPUT_FILE}': {e}")
        sys.exit(1)

    logger.info("All AI automated file modifications applied.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
