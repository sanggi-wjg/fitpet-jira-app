import requests
from colorful_print import cp
from jira import JIRA, Issue, JIRAError
from jira.resources import Version
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from fitpet_jira.config import JiraConfig
from fitpet_jira.models import JiraVersionKey


class JiraClient:
    def __init__(self, config: JiraConfig):
        self.jira = JIRA(
            server=config.server,
            basic_auth=(config.username.get_secret_value(), config.token.get_secret_value()),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=3, max=10),
        retry=retry_if_exception_type((JIRAError, requests.exceptions.ReadTimeout)),
        reraise=True,
    )
    def find_issue(self, issue_id: str) -> Issue:
        try:
            return self.jira.issue(issue_id)
        except JIRAError as e:
            cp.red(f"이슈를 찾지 못했습니다: '{issue_id}' ({e.status_code}, {e.text})")
            raise e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=3, max=10),
        retry=retry_if_exception_type((JIRAError, requests.exceptions.ReadTimeout)),
        reraise=True,
    )
    def find_unreleased_versions(self, project: str, version_keys: list[JiraVersionKey]) -> list[Version]:
        try:
            versions: list[Version] = self.jira.project_versions(project)
            return [version for version in versions if _is_unreleased_version(version, version_keys)]
        except JIRAError as e:
            cp.red(f"버전 목록을 찾지 못했습니다: project={project}, version_keys={version_keys}")
            raise e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=3, max=10),
        retry=retry_if_exception_type((JIRAError, requests.exceptions.ReadTimeout)),
        reraise=True,
    )
    def find_latest_released_version(self, project: str, version_key: JiraVersionKey) -> Version | None:
        try:
            versions: list[Version] = self.jira.project_versions(project)
            released_versions = [version for version in versions if _is_released_version(version, version_key)]
            if not released_versions:
                return None

            return max(
                released_versions,
                key=lambda version: version.releaseDate,
            )
        except JIRAError as e:
            cp.red(f"최신 릴리스 버전을 찾지 못했습니다: project={project}, version_key={version_key}")
            raise e

    def create_version(self, project: str, release_name: str) -> Version:
        # 생성은 재시도 X
        try:
            return self.jira.create_version(project=project, name=release_name)
        except JIRAError as e:
            cp.red(
                f"릴리스 버전을 생성하지 못했습니다: project={project}, name={release_name} ({e.status_code}, {e.text})"
            )
            raise e


def _is_unreleased_version(version: Version, version_keys: list[JiraVersionKey]) -> bool:
    return not version.released and not version.archived and any(key in version.name for key in version_keys)


def _is_released_version(version: Version, version_key: JiraVersionKey) -> bool:
    return version.released and not version.archived and hasattr(version, "releaseDate") and version_key in version.name
