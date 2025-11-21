from colorful_print import cp
from jira import JIRA, JIRAError, Issue
from jira.resources import Version


class JiraClient:

    def __init__(self, server: str, username: str, token: str):
        self.jira = JIRA(server=server, basic_auth=(username, token))

    def find_issue(self, issue_id: str) -> Issue:
        try:
            return self.jira.issue(issue_id)
        except JIRAError as e:
            cp.red(f"Could not find issue '{issue_id}': {e.status_code}, {e.text}")
            raise

    def find_unreleased_versions(self, project: str, version_key: list[str]) -> list[Version]:
        try:
            versions = self.jira.project_versions(project)
            return [
                version
                for version in versions
                if not version.released and not version.archived and any(key in version.name for key in version_key)
            ]

        except JIRAError:
            cp.red(f"Could not find versions by project: {project}, version_key: {version_key}")
            raise
