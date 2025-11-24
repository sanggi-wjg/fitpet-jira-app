import pytest
from jira import Issue
from jira.resources import Version

from fitpet_jira import jira_client
from fitpet_jira.config import JiraConfig

TEST_JIRA_CONFIG = JiraConfig(
    jira_server="https://test-jira.atlassian.net",
    jira_project="FMP",
    jira_username="test@example.com",
    jira_token="test-token-12345",
)


def _create_mock_issue(mocker, _id: str = "FMP-1234") -> Issue:
    mock_issue = mocker.create_autospec(Issue, instance=True)
    mock_issue.key = _id
    return mock_issue


def _create_mock_version(
    mocker,
    version_id: str,
    name: str,
    released: bool = False,
    archived: bool = False,
) -> Version:
    mock_version = mocker.create_autospec(Version, instance=True)
    mock_version.id = version_id
    mock_version.name = name
    mock_version.released = released
    mock_version.archived = archived
    return mock_version


@pytest.fixture
def mock_issue(mocker):
    return _create_mock_issue(mocker)


@pytest.fixture
def mock_versions(mocker):
    return [
        _create_mock_version(mocker, "1", "1.0.0-ADMIN-release", released=False, archived=False),
        _create_mock_version(mocker, "2", "1.0.0-CONSUMER-release", released=False, archived=False),
        _create_mock_version(mocker, "3", "1.0.0-SELLER-release", released=True, archived=False),  # released
        _create_mock_version(mocker, "4", "1.0.0-API-release", released=False, archived=True),  # archived
        _create_mock_version(mocker, "5", "1.0.0-BATCH-release", released=False, archived=False),
    ]


@pytest.fixture
def mock_jira(mocker):
    return mocker.patch.object(jira_client, "JIRA")
