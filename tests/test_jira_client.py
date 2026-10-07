import pytest
from jira import JIRAError

from fitpet_jira.jira_client import JiraClient
from fitpet_jira.models import JiraVersionKey
from tests.conftest import TEST_JIRA_CONFIG, _create_mock_version


class TestJiraClient:
    @classmethod
    def setup_class(cls):
        cls.test_jira_config = TEST_JIRA_CONFIG

    def test_init(self, mock_jira):
        JiraClient(self.test_jira_config)

        # SecretStr 이 아닌 실제 값이 인증에 전달되어야 한다
        mock_jira.assert_called_once_with(
            server="https://test-jira.atlassian.net",
            basic_auth=("test@example.com", "test-token-12345"),
        )

    def test_find_issue_success(self, mock_jira, mock_issue):
        jira_client = JiraClient(self.test_jira_config)

        # mock
        mock_jira.return_value.issue.return_value = mock_issue

        result = jira_client.find_issue(mock_issue.key)
        assert result.key == mock_issue.key

    def test_find_issue_failure(self, mock_jira, mock_issue):
        jira_client = JiraClient(self.test_jira_config)

        # mock
        mock_jira.return_value.issue.side_effect = JIRAError(
            status_code=404,
            text="Issue Does Not Exist",
        )

        with pytest.raises(JIRAError) as exc_info:
            jira_client.find_issue("NOTHING")
            assert exc_info.value.status_code == 404

    def test_find_unrelease_versions(self, mock_jira, mock_versions):
        jira_client = JiraClient(self.test_jira_config)

        # mock
        mock_jira.return_value.project_versions.return_value = mock_versions

        result = jira_client.find_unreleased_versions("FMP", [JiraVersionKey.ADMIN, JiraVersionKey.CONSUMER])

        assert len(result) == 2

        version_names = [v.name for v in result]
        assert "1.0.0-ADMIN-release" in version_names
        assert "1.0.0-CONSUMER-release" in version_names

    def test_create_version_success(self, mock_jira):
        jira_client = JiraClient(self.test_jira_config)

        jira_client.create_version("FMP", "BE-MALL-LEGACY-3.13.7")

        mock_jira.return_value.create_version.assert_called_once_with(name="BE-MALL-LEGACY-3.13.7", project="FMP")

    def test_create_version_failure_not_retried(self, mock_jira):
        jira_client = JiraClient(self.test_jira_config)

        # mock
        mock_jira.return_value.create_version.side_effect = JIRAError(
            status_code=400,
            text="A version with this name already exists in this project.",
        )

        with pytest.raises(JIRAError):
            jira_client.create_version("FMP", "BE-MALL-LEGACY-3.13.7")

        assert mock_jira.return_value.create_version.call_count == 1

    def test_find_latest_released_version(self, mocker, mock_jira):
        jira_client = JiraClient(self.test_jira_config)

        # mock
        latest = _create_mock_version(mocker, "1", "BE-MALL-LEGACY-3.13.6", released=True, release_date="2026-10-01")
        older = _create_mock_version(mocker, "2", "BE-MALL-LEGACY-3.13.5", released=True, release_date="2026-09-01")
        no_release_date = _create_mock_version(mocker, "3", "BE-MALL-LEGACY-3.13.4", released=True)
        unreleased = _create_mock_version(mocker, "4", "BE-MALL-LEGACY-3.13.7", released=False)
        other_key = _create_mock_version(mocker, "5", "BE-MALL-ADMIN-9.9.9", released=True, release_date="2026-10-05")
        mock_jira.return_value.project_versions.return_value = [older, no_release_date, latest, unreleased, other_key]

        result = jira_client.find_latest_released_version("FMP", JiraVersionKey.LEGACY)

        assert result is not None
        assert result.name == "BE-MALL-LEGACY-3.13.6"

    def test_find_latest_released_version_not_found(self, mocker, mock_jira):
        jira_client = JiraClient(self.test_jira_config)

        # mock
        mock_jira.return_value.project_versions.return_value = [
            _create_mock_version(mocker, "1", "BE-MALL-LEGACY-3.13.7", released=False),
            _create_mock_version(mocker, "2", "BE-MALL-ADMIN-1.0.0", released=True),
        ]

        assert jira_client.find_latest_released_version("FMP", JiraVersionKey.LEGACY) is None
