from jprcfai import (
    execute_major_coding_task,
    fix_single_code_file,
    apply_changes_to_code,
    execute_python_command,
    ERROR_AFTER_TIMER,
)

import tempfile
import os
import shutil


def create_temporary_directory_from(directory):
    """
    Creates a temporary directory and copies all the contents from the given
    directory into it. Returns the path to the temporary directory.
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Iterate over all items in the source directory
    for item in os.listdir(directory):
        src_path = os.path.join(directory, item)
        dest_path = os.path.join(temp_dir, item)
        if os.path.isdir(src_path):
            # Copy the directory recursively
            shutil.copytree(src_path, dest_path)
        else:
            # Copy a file preserving metadata
            shutil.copy2(src_path, dest_path)

    return temp_dir


def create_empty_directory():
    """
    Creates an empty temporary directory and returns its path.
    """
    temp_dir = tempfile.mkdtemp()
    return temp_dir


def test_single_code_file(capsys):
    with open("tests/files/wrong_regex.py", "r") as f:
        file_code = f.read()
    fix_single_code_file(file_code, "python3", "codex-medium", 10, ERROR_AFTER_TIMER)


def test_modify_single_file(capsys):
    with open("tests/files/add_numbers.py", "r") as f:
        file_code = f.read()

    requested_changes = (
        "Modify the arguments used in the add function from (5, 6) to (10, 21)"
    )
    new_file_code = apply_changes_to_code(
        file_code, requested_changes, "codex-medium", False
    )
    result = execute_python_command(new_file_code, directory=".")

    assert result == "31\n", f"Expected output: '31\n', got: '{result}'"


def test_big_task_from_scratch(capsys):
    # Create a temporary copy of the target directory.
    temp_project_dir = create_empty_directory()

    # Now run the coding task against the temporary directory.
    # This ensures that the original directory is not modified.
    execute_major_coding_task(
        "Create a python script that reads using the 'open' function a local (project root directory) "
        "README.md with the content 'buenos dias' without the character ' and prints its content.",
        temp_project_dir,
        "python3 index.py",
    )

    # --- Additional Assertions ---

    # 1. Check if README.md exists and contains the correct content.
    readme_path = os.path.join(temp_project_dir, "README.md")
    assert os.path.exists(readme_path), (
        "README.md does not exist in the temporary project directory."
    )
    with open(readme_path, "r", encoding="utf-8") as file:
        readme_content = file.read().strip()
    assert readme_content == "buenos dias", (
        f"README.md content expected to be 'buenos dias', got: '{readme_content}'"
    )

    # 2. Check if index.py exists.
    index_path = os.path.join(temp_project_dir, "index.py")
    assert os.path.exists(index_path), (
        "index.py does not exist in the temporary project directory."
    )

    # 3. Check if index.py contains the string: open("README.md", "r")
    with open(index_path, "r", encoding="utf-8") as file:
        index_content = file.read()
    assert "open(" in index_content, "index.py must contain a call to open()"
    assert "README.md" in index_content, "index.py must refer to 'README.md'"

    shutil.rmtree(temp_project_dir)


def test_big_task(capsys):
    temp_project_dir = create_temporary_directory_from("tests/files/initial_project")

    execute_major_coding_task(
        "Change all .json files to .yaml files, these should have the yaml structure and their content should be the equivalent as the original json files. "
        "The new .yaml files CANNOT have json structure, they should be in the equivalent yaml format. no '{' or '}' allowed. "
        "The parse_files.py keep a similar logic but instead of the tuple (.json, .txt), now would be (.yaml, .txt). "
        "The team calculated the expect output for the test command and after the changes it should be (60, 37) due to the json to yaml files conversion. ",
        temp_project_dir,
        "python3 parse_files.py",
    )

    assert os.path.exists(os.path.join(temp_project_dir, "parse_files.py"))
    assert os.path.exists(os.path.join(temp_project_dir, "users.yaml"))
    assert os.path.exists(os.path.join(temp_project_dir, "configuration.txt"))

    with open(
        os.path.join(temp_project_dir, "users.yaml"), "r", encoding="utf-8"
    ) as file:
        yaml_content = file.read()
    assert "{" not in yaml_content, "users.yaml should not contain '{'"
    assert "}" not in yaml_content, "users.yaml should not contain '}'"

    assert not os.path.exists(os.path.join(temp_project_dir, "users.json")), (
        "users.json should not exist"
    )
