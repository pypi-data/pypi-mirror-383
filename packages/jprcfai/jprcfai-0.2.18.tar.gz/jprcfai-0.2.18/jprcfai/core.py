#!/usr/bin/env python3
import os
import re
import subprocess
import webbrowser
import tempfile
import requests
import shutil
import sys
import json  # Added import json for caching mechanism
from pathlib import Path
from platformdirs import user_cache_dir
import shlex
import time
from typing import Optional, Set, Dict, Tuple, Any, Union

# Define a type alias for cache entries.
CacheEntry = Dict[str, Union[str, float]]


def load_prompt_cache() -> Dict[str, CacheEntry]:
    """
    Loads the prompt cache from the user cache directory for jprcfai,
    and purges expired entries (where the expiration time has passed).
    """
    cache_dir: str = user_cache_dir("jprcfai")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file: str = os.path.join(cache_dir, "prompt_cache.json")
    cache: Dict[str, CacheEntry] = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception as e:
            print(f"Error loading prompt cache: {e}")
    # Purge expired or invalid entries:
    now: float = time.time()
    for key in list(cache.keys()):
        entry: Any = cache.get(key)
        if not isinstance(entry, dict) or "expiration" not in entry:
            del cache[key]
        elif now > entry["expiration"]:
            del cache[key]
    return cache


def save_prompt_cache(cache: Dict[str, CacheEntry]) -> None:
    """
    Saves the prompt cache to the user cache directory for jprcfai.
    """
    cache_dir: str = user_cache_dir("jprcfai")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file: str = os.path.join(cache_dir, "prompt_cache.json")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"Error saving prompt cache: {e}")


def get_cached_value(key_str: str) -> Optional[str]:
    """
    Returns the cached value for key_str if it exists and is not expired.
    Otherwise returns None.
    """
    global PROMPT_CACHE
    entry: Optional[Any] = PROMPT_CACHE.get(key_str)
    if entry is None:
        return None
    if not isinstance(entry, dict) or "expiration" not in entry:
        PROMPT_CACHE.pop(key_str, None)
        save_prompt_cache(PROMPT_CACHE)
        return None
    if time.time() > entry["expiration"]:
        # Entry expired, remove it.
        PROMPT_CACHE.pop(key_str, None)
        save_prompt_cache(PROMPT_CACHE)
        return None
    return entry["value"]


def set_cached_value(key_str: str, value: str) -> None:
    """
    Sets the value in the cache with an expiration time (5 minutes from now).
    """
    global PROMPT_CACHE
    expiration_time: float = time.time() + 300  # 300 seconds = 5 minutes
    PROMPT_CACHE[key_str] = {"value": value, "expiration": expiration_time}
    save_prompt_cache(PROMPT_CACHE)


PROMPT_CACHE: Dict[str, CacheEntry] = load_prompt_cache()


def ask_openai(user_prompt: str, reasoning_effort: str) -> Optional[str]:
    """
    Sends the user_prompt to the OpenAI API and returns the answer.
    This function centralizes the API request logic to avoid duplication.
    """
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
    }
    effort = (
        reasoning_effort[6:]
        if reasoning_effort.startswith("codex-")
        else reasoning_effort
    )
    model = "gpt-5-codex" if reasoning_effort.startswith("codex-") else "gpt-5-mini"

    payload: Dict[str, Any] = {
        "model": model,
        "input": user_prompt,
        "store": False,
        "reasoning": {"effort": effort},
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json=payload,
            timeout=300,
        )
        # If the status code indicates an error, raise an exception.
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        try:
            # Try to parse the JSON response to get more details.
            error_json = response.json()
            error_message = error_json.get("error", {}).get(
                "message", "No error message provided"
            )
        except ValueError:
            # If response is not JSON, use the text.
            error_message = response.text
        print(f"HTTP error occurred: {http_err}\nDetails: {error_message}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request to OpenAI failed:\n{req_err}")
        return None

    response_json: Dict[str, Any] = response.json()
    if "output" not in response_json or not response_json["output"]:
        print("Error: Unexpected response from OpenAI:", response_json)
        return None

    assistant_response = next(
        (
            element["content"]
            for element in response_json["output"]
            if element.get("role") == "assistant"
        ),
        None,
    )

    if assistant_response is None:
        print("Error: No assistant response found in the output.")
        return None

    text_content = next(
        (
            element["text"]
            for element in assistant_response
            if element.get("type") == "output_text"
        ),
        None,
    )

    if text_content is None:
        print("Error: No text content found in the assistant response.")
        return None

    return text_content


def ask_gemini(user_prompt: str, reasoning_effort: str) -> Optional[str]:
    """
    Sends `user_prompt` to the Google Gemini API and returns the answer.

    Parameters
    ----------
    user_prompt : str
        The text you want Gemini to answer.
    reasoning_effort : str
        One of {"pro", "flash", "lite"}.

    Returns
    -------
    Optional[str]
        The model’s response text, or None if any error occurs.
    """
    MODEL_MAP: Dict[str, str] = {
        "pro": "gemini-2.5-pro",
        "flash": "gemini-2.5-flash",
        "lite": "gemini-2.5-flash-lite",
    }

    effort = reasoning_effort.lower()
    if effort not in MODEL_MAP:
        raise ValueError(
            f"Invalid reasoning_effort '{reasoning_effort}'. "
            f"Choose one of {list(MODEL_MAP)}."
        )

    model_id = MODEL_MAP[effort]
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_id}:generateContent"
    )
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("Please set the GEMINI_API_KEY env variable.")

    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_prompt}],
            }
        ],
        "generationConfig": {"temperature": 0},
    }

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            params=params,
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        try:
            error_json = response.json()
            error_message = error_json.get("error", {}).get(
                "message", "No error message provided"
            )
        except ValueError:
            error_message = response.text
        print(f"HTTP error from Gemini: {http_err}\nDetails: {error_message}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request to Gemini failed:\n{req_err}")
        return None

    # Successful 200-series response
    response_json: Dict[str, Any] = response.json()
    try:
        return (
            response_json["candidates"][0]["content"]["parts"][0][
                "text"
            ].lstrip()  # remove leading newline if present
        )
    except (KeyError, IndexError, TypeError):
        print("Error: Unexpected response from Gemini:", response_json)
        return None


def unroll_prompt_from_file(
    filename: str, dir: Optional[str] = None, unroll: bool = False
) -> str:
    """
    Reads the file content from a directory specified by the
    ASSISTANTS_DIR environment variable.
    """
    base_dir: str = dir if dir else os.environ.get("ASSISTANTS_DIR", "")
    filepath: str = os.path.join(base_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content: str = f.read()
    return unroll_prompt(content) if unroll else content


def get_repo_name(git_url: str) -> str:
    """
    Extracts the repository name from a git URL.
    For example, given "git@github.com:username/repo.git" or
    "https://github.com/username/repo.git" it returns "repo".
    """
    # Handle SSH-style URL (with colon)
    if "@" in git_url and ":" in git_url:
        part: str = git_url.split(":")[-1]  # e.g., "username/repo.git"
    else:
        # Handle HTTPS-style URL.
        part = git_url.rstrip("/").split("/")[-1]
    if part.endswith(".git"):
        part = part[:-4]
    return part


def unroll_prompt_from_git(git_url: str, file_location: str, branch: str) -> str:
    """
    Clones (or updates) a repository in a user-specific cache folder,
    then retrieves the content of a file from the specified branch.
    """
    repo_name: str = get_repo_name(git_url)

    # 1) Determine the user cache directory for your project:
    cache_dir: str = user_cache_dir("jprcfai")
    repos_dir: str = os.path.join(cache_dir, "repos")
    os.makedirs(repos_dir, exist_ok=True)

    # 2) Clone or update the repo inside the cache directory.
    repo_path: str = os.path.join(repos_dir, repo_name)
    git_cmd: Optional[str] = shutil.which("git")
    if not git_cmd:
        raise EnvironmentError("Git is not installed or not found in PATH.")

    if not os.path.exists(repo_path):
        subprocess.run([git_cmd, "clone", git_url, repo_path], check=True)
    else:
        subprocess.run([git_cmd, "-C", repo_path, "fetch"], check=True)

    # 3) Use 'git show' to grab the file contents.
    result = subprocess.run(
        [git_cmd, "-C", repo_path, "show", f"{branch}:{file_location}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def unroll_prompt(prompt: str, visited: Optional[Set[Any]] = None) -> str:
    """
    Recursively replaces placeholders in the prompt with their loaded content.

    There are three placeholder types:

    1. [#PLACEHOLDER_LOAD_FROM_FILE (<prompt_label>)]
       -> Loads content from a local file.

    2. [#PLACEHOLDER_LOAD_FILE_FROM_GIT (<git_url_ssh>, <file_location>, <branch>)]
       -> Clones or updates a git repository and loads content from a file in that repo.

    3. [#PLACEHOLDER_LOAD_CONTENT_FROM_SCRIPT_EXECUTION ([<full_command>], <is_custom_dir>)]
       -> Executes the provided script command, captures its output, and recursively
          processes any placeholders within that output.
          If <is_custom_dir> is False, the script is assumed to be internal to the package
          (jprcfai) and its path is resolved relative to the package's assistants directory.

    Caching Enhancement:
    This function now uses a persistent cache stored in the user cache directory for 'jprcfai'.
    Each cached item is stored with an expiration time 5 minutes from the moment of caching.
    Expired items are not used and are removed from the cache.
    """
    global PROMPT_CACHE

    if visited is None:
        visited = set()  # type: Set[Any]

    # Regular expression for file-based placeholders:
    file_pattern: re.Pattern = re.compile(
        r"\[#PLACEHOLDER_LOAD_FROM_FILE\s*\(\s*([^)]+?)\s*\)\]"
    )
    # Regular expression for git-based placeholders:
    git_pattern: re.Pattern = re.compile(
        r"\[#PLACEHOLDER_LOAD_FILE_FROM_GIT\s*\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*([^)]+?)\s*\)\]"
    )
    # Regular expression for script execution placeholders:
    script_pattern: re.Pattern = re.compile(
        r"\[#PLACEHOLDER_LOAD_CONTENT_FROM_SCRIPT_EXECUTION\s*\(\s*\[\s*([^\]]+?)\s*\]\s*,\s*([^)]+?)\s*\)\]"
    )

    def file_repl(match: re.Match) -> str:
        filename: str = match.group(1).strip()
        key: Tuple[str, str] = ("LOAD_FROM_FILE", filename)
        if key in visited:
            return match.group(0)
        visited.add(key)
        try:
            content: str = unroll_prompt_from_file(filename)
        except Exception as e:
            content = f"[Error loading file '{filename}': {e}]"
        # Process any placeholders within the loaded content recursively.
        result_value: str = unroll_prompt(content, visited)
        return result_value

    def git_repl(match: re.Match) -> str:
        git_url: str = match.group(1).strip()
        file_location: str = match.group(2).strip()
        branch: str = match.group(3).strip()
        key: Tuple[str, str, str, str] = (
            "LOAD_FROM_GIT",
            git_url,
            file_location,
            branch,
        )
        key_str: str = json.dumps(key)
        ignore_cache: bool = (
            os.environ.get("JPRCFAI_IGNORE_CACHE", "False").lower() == "true"
        )
        if not ignore_cache:
            cached: Optional[str] = get_cached_value(key_str)
            if cached is not None:
                return cached
        if key in visited:
            return match.group(0)
        visited.add(key)
        try:
            content: str = unroll_prompt_from_git(git_url, file_location, branch)
        except Exception as e:
            content = (
                f"[Error loading from git ({git_url}, {file_location}, {branch}): {e}]"
            )
        # Recursively process the loaded content.
        result_value: str = unroll_prompt(content, visited)
        if not ignore_cache:
            set_cached_value(key_str, result_value)
        return result_value

    def script_repl(match: re.Match) -> str:
        full_command_str: str = match.group(1).strip()
        is_custom_dir_str: str = match.group(2).strip()
        # Convert the is_custom_dir string to a boolean.
        is_custom_dir: bool = is_custom_dir_str.lower() == "true"
        key: Tuple[str, str, bool] = (
            "LOAD_FROM_SCRIPT",
            full_command_str,
            is_custom_dir,
        )
        if key in visited:
            return match.group(0)
        visited.add(key)
        try:
            posix_mode: bool = sys.platform != "win32"
            tokens: Any = shlex.split(full_command_str, posix=posix_mode)
            # If not a custom directory, assume the script is internal to the package,
            # and resolve its path relative to this file using pathlib.
            if not is_custom_dir and len(tokens) > 1:
                # tokens[1] is assumed to be a relative script path.
                script_path: Path = Path(__file__).parent / tokens[1]
                tokens[1] = str(script_path.resolve())
            result = subprocess.run(tokens, capture_output=True, text=True, check=True)
            content = result.stdout
        except Exception as e:
            content = f"[Error executing script command ('{full_command_str}', {is_custom_dir_str}): {e}]"
        # Recursively process any placeholders within the output.
        result_value: str = unroll_prompt(content, visited)
        return result_value

    # First, replace any file-based placeholders.
    prompt = file_pattern.sub(file_repl, prompt)
    # Then, replace any git-based placeholders.
    prompt = git_pattern.sub(git_repl, prompt)
    # Finally, replace any script execution placeholders.
    prompt = script_pattern.sub(script_repl, prompt)

    return prompt


def execute_local_script_with_browser(
    code: str, execution_command: str, port: int
) -> None:
    """
    Executes the provided code by writing it to a temporary file and launching it
    using the given command. Immediately launches the default web browser to the specified port.

    Parameters:
      code: The code to execute.
      execution_command: Command to execute the code (e.g., "node").
      port: Port number for launching the browser.
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".js", encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(code)
            tmp_filepath: str = tmp_file.name
    except Exception as exc:
        print("Failed to write to temporary file:", exc)
        return

    # Ensure the execution command is available
    exec_cmd: Optional[str] = shutil.which(execution_command)
    if not exec_cmd:
        print(f"Error: {execution_command} is not installed or not found in PATH.")
        return

    print("\nExecuting final code from temporary file:", tmp_filepath)
    process = subprocess.Popen(
        [exec_cmd, tmp_filepath],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    webbrowser.open(f"http://localhost:{port}")
    print(f"\nBrowser launched to http://localhost:{port}.")

    process.wait()

    try:
        os.unlink(tmp_filepath)
    except Exception as e:
        print(f"Warning: Could not delete temporary file {tmp_filepath}: {e}")
