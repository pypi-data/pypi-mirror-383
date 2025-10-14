from .core import ask_openai, unroll_prompt_from_file, unroll_prompt
from .logger_config import logger, reevaluate_logger_configuration
import subprocess
import tempfile
import os
import shutil
from typing import Optional

ERROR_AFTER_TIMER: str = (
    "ERROR_AFTER_TIMER"  # For servers: after wait_time, process must be running.
)
OK_AFTER_TIMER: str = "OK_AFTER_TIMER"  # For servers: after wait_time, if no errors are detected, it is considered OK.
WAIT_UNTIL_FINISH: str = "WAIT_UNTIL_FINISH"  # Always wait until the process finishes.


def fix_single_code_file(
    answer: str,
    execution_command: str,
    reasoning_effort: str,
    wait_time: Optional[float],
    mode: str,
    max_retries: int = 5,
) -> Optional[str]:
    """
    Iteratively writes the provided code (answer) to a temporary file, launches it using the specified
    execution_command, checks for startup errors according to the specified wait_time and mode, and,
    if errors are detected, attempts to fix them by sending an update request to OpenAI.
    The temporary file is deleted after execution.

    Parameters:
      answer (str): The code to execute.
      execution_command (str): Command to execute the code (e.g., "node").
      reasoning_effort (str): The reasoning effort for execution (error fixes use 'medium').
      wait_time (Optional[float]): Time in seconds to wait after process launch to check status.
                                   If None, waits until the process finishes.
      mode (str): One of the following modes:
                  ERROR_AFTER_TIMER: For servers. After wait_time seconds, process must have finished (with exit code 0).
                  OK_AFTER_TIMER: For scripts. After wait_time seconds, if no errors are detected, it is considered OK.
                  WAIT_UNTIL_FINISH: Waits for the process to finish, then checks the exit code.
      max_retries (int, optional): Maximum number of retries allowed (default is 5).
    Returns:
      Optional[str]: The final code (answer) that was executed successfully, or None if execution fails after maximum retries.
    """

    reevaluate_logger_configuration()
    attempts: int = 0
    while attempts < max_retries:
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".js", encoding="utf-8"
            ) as tmp_file:
                tmp_file.write(answer)
                tmp_filepath: str = tmp_file.name
        except Exception as exc:
            logger.error("Failed to write to temporary file:", exc)
            return None

        # Ensure the execution command is available
        exec_cmd: Optional[str] = shutil.which(execution_command)
        if not exec_cmd:
            logger.error(
                f"Error: {execution_command} is not installed or not found in PATH."
            )
            return None

        logger.info(f"Launching with '{exec_cmd} {tmp_filepath}' ...")

        process = subprocess.Popen(
            [exec_cmd, tmp_filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        success: bool = False
        error_message: str = ""

        if wait_time is not None and mode != WAIT_UNTIL_FINISH:
            if mode == ERROR_AFTER_TIMER:
                # Use wait(timeout=...) to check if the process finishes in time.
                try:
                    ret: int = process.wait(timeout=wait_time)
                    if ret == 0:
                        success = True
                    else:
                        outs, errs = process.communicate()
                        error_message = (
                            errs.strip()
                            if errs.strip()
                            else f"{execution_command} exited with code {ret}"
                        )
                        logger.info(
                            f"\nError detected: Process terminated in ERROR_AFTER_TIMER mode:\n{error_message}"
                        )
                except subprocess.TimeoutExpired:
                    # Process did not finish in time.
                    process.terminate()
                    process.wait()
                    error_message = f"{execution_command} did not finish within {wait_time} seconds."
                    logger.info(f"\nError detected: {error_message}")

            elif mode == OK_AFTER_TIMER:
                try:
                    ret: int = process.wait(timeout=wait_time)
                    if ret == 0:
                        success = True
                    else:
                        outs, errs = process.communicate()
                        error_message = (
                            errs.strip()
                            if errs.strip()
                            else f"{execution_command} exited with code {ret}"
                        )
                        logger.info(
                            f"\nError detected in OK_AFTER_TIMER mode:\n{error_message}"
                        )
                except subprocess.TimeoutExpired:
                    # Process is still running after wait_time which is acceptable in OK_AFTER_TIMER.
                    success = True
                    process.terminate()
                    process.wait()

        else:
            # WAIT_UNTIL_FINISH mode or no wait_time provided.
            retcode: int = process.wait()
            if retcode == 0:
                success = True
            else:
                outs, errs = process.communicate()
                error_message = (
                    errs.strip()
                    if errs.strip()
                    else f"{execution_command} exited with code {retcode}"
                )
                logger.info(
                    f"\nError detected in WAIT_UNTIL_FINISH mode:\n{error_message}"
                )

        try:
            os.unlink(tmp_filepath)
        except Exception as e:
            logger.error(
                f"Warning: Could not delete temporary file {tmp_filepath}: {e}"
            )

        if success:
            logger.info(
                f"\n{execution_command} executed successfully under mode {mode}."
            )
            return answer
        else:
            attempts += 1
            logger.info(
                f"\nAttempt {attempts}/{max_retries}: Error encountered. Attempting to fix the error by updating the code with reasoning set to '{reasoning_effort}'..."
            )
            fix_file_content: str = unroll_prompt_from_file("CodeFixer.txt")
            fix_file_content = unroll_prompt(fix_file_content)
            new_user_prompt: str = fix_file_content.replace("[FILE_CODE]", answer)
            new_user_prompt = new_user_prompt.replace("[ERROR]", error_message)
            new_user_prompt = new_user_prompt.replace(
                "[EXECUTE_COMMAND]", execution_command + " " + tmp_filepath
            )
            new_answer: Optional[str] = ask_openai(new_user_prompt, reasoning_effort)
            if new_answer is None:
                logger.error("Failed to receive a fixed code from OpenAI. Exiting.")
                return None
            answer = new_answer
            logger.info("Updated code received. Retrying execution...\n")

    logger.info("Maximum retries reached in fix_single_code_file. Exiting.")
    return None
