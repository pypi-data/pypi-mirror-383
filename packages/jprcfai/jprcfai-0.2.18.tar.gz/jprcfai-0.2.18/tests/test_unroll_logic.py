from jprcfai.core import unroll_prompt_from_file


def test_unroll_file(capsys):
    with capsys.disabled():
        check_point_status = unroll_prompt_from_file("CheckpointStatus.txt")

        # no scheduled placeholders on CheckpointStatus.txt
        assert check_point_status == unroll_prompt_from_file(
            "CheckpointStatus.txt", unroll=True
        )

        checkpointer_redirecter_raw = unroll_prompt_from_file(
            "CheckpointerRedirecter.txt", unroll=False
        )

        checkpointer_redirecter = unroll_prompt_from_file(
            "CheckpointerRedirecter.txt", unroll=True
        )

        excepted_checkpointer_redirecter = checkpointer_redirecter_raw.replace(
            "[#PLACEHOLDER_LOAD_FROM_FILE (CheckpointStatus.txt)]", check_point_status
        )

        assert checkpointer_redirecter == excepted_checkpointer_redirecter
