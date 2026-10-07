import pytest
from jira import JIRAError

from fitpet_jira.jira_client import JiraClient
from fitpet_jira.models import JiraVersionKey
from tests.conftest import TEST_JIRA_CONFIG


class TestJiraClient:
    @classmethod
    def setup_class(cls):
        cls.test_jira_config = TEST_JIRA_CONFIG

    def test_init(self, mock_jira):
        JiraClient(
            server=self.test_jira_config.jira_server,
            username=self.test_jira_config.jira_username,
            token=self.test_jira_config.jira_token,
        )

        mock_jira.assert_called_once_with(
            server=self.test_jira_config.jira_server,
            basic_auth=(
                self.test_jira_config.jira_username,
                self.test_jira_config.jira_token,
            ),
        )

    def test_find_issue_success(self, mock_jira, mock_issue):
        jira_client = JiraClient(
            server=self.test_jira_config.jira_server,
            username=self.test_jira_config.jira_username,
            token=self.test_jira_config.jira_token,
        )

        # mock
        mock_jira.return_value.issue.return_value = mock_issue

        result = jira_client.find_issue(mock_issue.key)
        assert result.key == mock_issue.key

    def test_find_issue_failure(self, mock_jira, mock_issue):
        jira_client = JiraClient(
            server=self.test_jira_config.jira_server,
            username=self.test_jira_config.jira_username,
            token=self.test_jira_config.jira_token,
        )

        # mock
        mock_jira.return_value.issue.side_effect = JIRAError(
            status_code=404,
            text="Issue Does Not Exist",
        )

        with pytest.raises(JIRAError) as exc_info:
            jira_client.find_issue("NOTHING")
            assert exc_info.value.status_code == 404

    def test_find_unrelease_versions(self, mock_jira, mock_versions):
        jira_client = JiraClient(
            server=self.test_jira_config.jira_server,
            username=self.test_jira_config.jira_username,
            token=self.test_jira_config.jira_token,
        )

        # mock
        mock_jira.return_value.project_versions.return_value = mock_versions

        result = jira_client.find_unreleased_versions("FMP", [JiraVersionKey.ADMIN, JiraVersionKey.CONSUMER])

        assert len(result) == 2

        version_names = [v.name for v in result]
        assert "1.0.0-ADMIN-release" in version_names
        assert "1.0.0-CONSUMER-release" in version_names

    def test_create_version_success(self, mock_jira):
        jira_client = JiraClient(
            server=self.test_jira_config.jira_server,
            username=self.test_jira_config.jira_username,
            token=self.test_jira_config.jira_token,
        )

        jira_client.create_version("FMP", "BE-MALL-LEGACY-3.13.7")

        mock_jira.return_value.create_version.assert_called_once_with(name="BE-MALL-LEGACY-3.13.7", project="FMP")

    def test_create_version_failure_not_retried(self, mock_jira):
        jira_client = JiraClient(
            server=self.test_jira_config.jira_server,
            username=self.test_jira_config.jira_username,
            token=self.test_jira_config.jira_token,
        )

        # mock
        mock_jira.return_value.create_version.side_effect = JIRAError(
            status_code=400,
            text="A version with this name already exists in this project.",
        )

        with pytest.raises(JIRAError):
            jira_client.create_version("FMP", "BE-MALL-LEGACY-3.13.7")

        assert mock_jira.return_value.create_version.call_count == 1
