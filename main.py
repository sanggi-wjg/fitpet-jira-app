import argparse
from typing import Callable

from colorful_print import cp

from fitpet_jira.config import Command, JiraConfig, CommandReqeust
from fitpet_jira.jira_client import JiraClient
from fitpet_jira.utils import escape_issue_id, escape_version_key


def command_assign_version(jira_config: JiraConfig, command_request: CommandReqeust):
    jira_client = JiraClient(jira_config.jira_server, jira_config.jira_username, jira_config.jira_token)

    issue = jira_client.find_issue(command_request.jira_issue_id)
    cp.bright_green(f"Found issue {issue.key}")

    versions = jira_client.find_unreleased_versions(jira_config.jira_project, command_request.jira_version_key)
    if len(versions) == 0:
        cp.yellow(f"Could not find version by {command_request.pr_name}, so skipping.")
        return

    cp.bright_green(f"Assign version {[version.name for version in versions]} to issue {issue.key}")
    issue.update(
        fields={
            "fixVersions": [{"id": version.id} for version in versions],
        },
    )


def create_factory(command: Command) -> Callable[[JiraConfig, CommandReqeust], None]:
    if command == Command.ASSIGN_VERSION:
        return command_assign_version
    else:
        raise Exception(f"Unknown command: {command}")


def main(jira_config: JiraConfig, command_request: CommandReqeust):
    if not command_request.is_ready_to_go():
        cp.yellow(f"Skipping command '{command_request.command.value}': Missing issue ID or version key from PR name")
        return

    cp.bright_green(f"[+] Starting '{command_request.command.value}' for PR: {command_request.pr_name}", bold=True)
    create_factory(command_request.command)(jira_config, command_request)
    cp.bright_green(f"[+] Completed '{command_request.command.value}' successfully", bold=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handling arguments.")
    parser.add_argument("-c", "--command", type=str, required=True)
    parser.add_argument("-p", "--pr", type=str, required=True)
    parser.add_argument("-js", "--server", type=str, required=True)
    parser.add_argument("-jp", "--project", type=str, required=True)
    parser.add_argument("-ju", "--username", type=str, required=True)
    parser.add_argument("-jt", "--token", type=str, required=True)
    args = parser.parse_args()

    config = JiraConfig(
        jira_server=args.server,
        jira_project=args.project,
        jira_username=args.username,
        jira_token=args.token,
    )
    request = CommandReqeust(
        command=Command(args.command),
        pr_name=args.pr,
        jira_issue_id=escape_issue_id(args.pr),
        jira_version_key=escape_version_key(args.pr),
    )
    main(config, request)
