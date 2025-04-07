import argparse
import enum
import re
from dataclasses import dataclass, field
from typing import Literal, Callable, List

from colorful_print import color
from jira import JIRA, JIRAError, Issue
from jira.resources import Version


class Command(enum.Enum):
    ASSIGN_VERSION = "assign_version"


@dataclass(frozen=True, slots=True, init=True)
class Config:
    command: Literal[Command.ASSIGN_VERSION] = field(metadata={"help": "실행 명령어"})
    pr_name: str = field(
        metadata={"help": "Github Pull Request 이름 ([FMP-1234] [ADMIN,CONSUMER] 상품 조회 및 consumer"}
    )
    jira_server: str = field(metadata={"help": "Jira Server"})
    jira_project: str = field(metadata={"help": "Jira Project"})
    jira_username: str = field(metadata={"help": "Jira Username"})
    jira_token: str = field(metadata={"help": "Jira Token"})

    jira_issue_key: str = field(metadata={"help": "PR 이름으로 issue_key 를 찾습니다."})
    jira_version_key: List[Literal["API", "ADMIN", "SELLER", "CONSUMER", "BATCH"]] = field(
        metadata={"help": "PR 이름으로 version_key 를 찾습니다."}
    )


def find_issue(config: Config) -> Issue:
    try:
        jira = JIRA(server=config.jira_server, basic_auth=(config.jira_username, config.jira_token))
        return jira.issue(config.jira_issue_key)

    except JIRAError:
        raise Exception(f"Could not find issue.")


def find_unreleased_versions(config: Config) -> List[Version]:
    try:
        jira = JIRA(server=config.jira_server, basic_auth=(config.jira_username, config.jira_token))
        versions = jira.project_versions(config.jira_project)
        suspected_versions = [
            version
            for version in versions
            if not version.released
            and not version.archived
            and any(key in version.name for key in config.jira_version_key)
        ]
        return suspected_versions

    except JIRAError:
        raise Exception(f"Could not find versions.")


def command_assign_version(config: Config):
    issue = find_issue(config)
    versions = find_unreleased_versions(config)
    color.yellow(f"Assign version {[version.name for version in versions]} to issue {issue.key}")
    issue.update(fields={"fixVersions": [{"id": version.id} for version in versions]})


def create_factory(command: Command) -> Callable[[Config], None]:
    if command == Command.ASSIGN_VERSION.value:
        return command_assign_version
    else:
        raise Exception(f"Unknown command: {command}")


def escape_issue_key(text: str) -> str:
    match = re.search(r"\[([A-Z]+-\d+)]", text)
    if match:
        return match.group(1)

    return ""


def escape_version_key(text: str) -> List[Literal["API", "ADMIN", "SELLER", "CONSUMER", "BATCH"]]:
    match = re.search(r"\[([A-Z,\s]+)]", text)
    if match:
        roles = match.group(1)
        return [
            role.strip() for role in roles.split(",") if role.strip() in ["API", "ADMIN", "SELLER", "CONSUMER", "BATCH"]
        ]

    return []


def main(config: Config):
    if not config.jira_issue_key or not config.jira_version_key or len(config.jira_version_key) == 0:
        color.yellow(f"Skip Command: {config.command}. Reason: Could not parse issue or version key.")
        return

    color.green(f"Start Command: {config.command} with PR: {config.pr_name}")
    create_factory(config.command)(config)
    color.green(f"Finish Command: {config.command}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handling arguments.")
    parser.add_argument("-c", "--command", type=str, required=True)
    parser.add_argument("-p", "--pr", type=str, required=True)
    parser.add_argument("-js", "--server", type=str, required=True)
    parser.add_argument("-jp", "--project", type=str, required=True)
    parser.add_argument("-ju", "--username", type=str, required=True)
    parser.add_argument("-jt", "--token", type=str, required=True)

    args = parser.parse_args()
    parsed_config = Config(
        command=args.command,
        pr_name=args.pr,
        jira_server=args.server,
        jira_project=args.project,
        jira_username=args.username,
        jira_token=args.token,
        jira_issue_key=escape_issue_key(args.pr),
        jira_version_key=escape_version_key(args.pr),
    )
    main(parsed_config)
