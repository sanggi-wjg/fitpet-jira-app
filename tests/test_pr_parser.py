import pytest

from fitpet_jira.models import JiraVersionKey
from fitpet_jira.util.pr_parser import extract_issue_id, extract_version_keys


class TestPrParser:
    @pytest.mark.parametrize(
        "pr_name, expected",
        [
            ("[FMP-1234] [ADMIN,CONSUMER] Fix bug", "FMP-1234"),
            ("[ABC-999] Some description", "ABC-999"),
            ("No issue ID here", ""),
            ("FMP-1234 without brackets", ""),
        ],
    )
    def test_extract_issue_id(self, pr_name, expected):
        assert extract_issue_id(pr_name) == expected

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
    def test_extract_version_keys(self, pr_name, expected):
        assert extract_version_keys(pr_name) == expected

    @pytest.mark.parametrize("key", list(JiraVersionKey))
    def test_all_allowed_keys(self, key):
        assert extract_version_keys(f"[FMP-1234] [{key}] Fix bug") == [key]
