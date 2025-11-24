import pytest

from fitpet_jira.config import JIRA_VERSION_KEYS_ALLOWED
from fitpet_jira.utils import escape_issue_id, escape_version_key


class TestUtils:

    @pytest.mark.parametrize(
        "pr_name, expected",
        [
            ("[FMP-1234] [ADMIN,CONSUMER] Fix bug", "FMP-1234"),
            ("[ABC-999] Some description", "ABC-999"),
            ("No issue ID here", ""),
            ("FMP-1234 without brackets", ""),
        ],
    )
    def test_escape_issue_id(self, pr_name, expected):
        assert escape_issue_id(pr_name) == expected

    @pytest.mark.parametrize(
        "pr_name, expected",
        [
            ("[FMP-1234] [ADMIN] Fix bug", ["ADMIN"]),
            ("[FMP-1234] [ADMIN,CONSUMER,BATCH] Fix bug", ["ADMIN", "CONSUMER", "BATCH"]),
            ("[ADMIN] Fix bug", ["ADMIN"]),
            ("[ABC-999] Some description", []),
            ("No version key here", []),
        ],
    )
    def test_escape_version_key(self, pr_name, expected):
        assert escape_version_key(pr_name) == expected

    @pytest.mark.parametrize("key", JIRA_VERSION_KEYS_ALLOWED)
    def test_all_allowed_keys(self, key):
        assert escape_version_key(f"[FMP-1234] [{key}] Fix bug") == [key]
