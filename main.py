from typing import Annotated

import typer
from colorful_print import cp
from pydantic import SecretStr

from fitpet_jira.config import JiraConfig
from fitpet_jira.jira_client import JiraClient
from fitpet_jira.models import AssignVersionRequest, JiraVersionKey
from fitpet_jira.util.pr_parser import extract_issue_id, extract_version_keys
from fitpet_jira.util.version_name import bump_patch_version

app = typer.Typer()

JiraServerOption = Annotated[
    str, typer.Option("--server", envvar="JIRA_SERVER", help="Jira 서버 주소 (예시, https://xxx.atlassian.net)")
]
JiraProjectOption = Annotated[
    str, typer.Option("--project", envvar="JIRA_PROJECT", help="Jira 프로젝트 키 (예시, FMP)")
]
JiraUsernameOption = Annotated[str, typer.Option("--username", envvar="JIRA_USERNAME", help="Jira 계정 이메일")]
JiraTokenOption = Annotated[str, typer.Option("--token", envvar="JIRA_TOKEN", help="Jira API 토큰")]


@app.command(name="assign-version", help="PR을 적절한 지라 릴리즈 버전에 할당합니다")
def command_assign_version(
    server: JiraServerOption,
    project: JiraProjectOption,
    username: JiraUsernameOption,
    token: JiraTokenOption,
    pr: Annotated[
        str,
        typer.Option(
            "--pr",
            help="Github PR 이름 (예시, [FMP-1234] [ADMIN,CONSUMER] 상품 조회 API 구현) / "
            "띄워쓰기가 있으니 따움표로 감싸주는 것을 잊지말아주세요.",
        ),
    ],
):
    config = JiraConfig(
        server=server,
        project=project,
        username=SecretStr(username),
        token=SecretStr(token),
    )
    pr_name = pr.replace("`", "")
    request = AssignVersionRequest(
        pr_name=pr_name,
        jira_issue_id=extract_issue_id(pr_name),
        jira_version_keys=extract_version_keys(pr_name),
    )

    if not request.is_ready_to_go():
        cp.yellow("assign-version을 건너뜁니다: PR 이름에서 이슈 ID 또는 버전 키를 찾지 못했습니다")
        return

    client = JiraClient(config)
    issue = client.find_issue(request.jira_issue_id)
    cp.bright_green(f"이슈를 찾았습니다: {issue.key}")

    versions = client.find_unreleased_versions(config.project, request.jira_version_keys)
    if len(versions) == 0:
        cp.yellow(f"PR 이름에 해당하는 버전을 찾지 못해 건너뜁니다: {request.pr_name}")
        return

    cp.bright_green(f"이슈 {issue.key}에 버전을 할당합니다: {[version.name for version in versions]}")
    issue.update(
        fields={"fixVersions": [{"id": version.id} for version in versions]},
    )
    cp.bright_green("😎 작업 완료")


@app.command("create-release", help="신규 릴리즈를 생성합니다.")
def command_create_release(
    server: JiraServerOption,
    project: JiraProjectOption,
    username: JiraUsernameOption,
    token: JiraTokenOption,
    version_key: Annotated[JiraVersionKey, typer.Option("--version-key", help="릴리즈 버전 키")],
):
    jira_config = JiraConfig(
        server=server,
        project=project,
        username=SecretStr(username),
        token=SecretStr(token),
    )

    client = JiraClient(jira_config)
    latest_version = client.find_latest_released_version(jira_config.project, version_key)
    if latest_version is None:
        cp.red(f"기준이 될 릴리즈 버전을 찾지 못했습니다: version_key={version_key}")
        raise typer.Exit(code=1)

    cp.bright_green(f"최신 릴리즈 버전을 찾았습니다: {latest_version.name}")
    new_version = bump_patch_version(latest_version.name)

    cp.bright_green(f"새로운 릴리즈 버전을 생성합니다: {new_version}")
    client.create_version(jira_config.project, new_version)
    cp.bright_green("😎 작업 완료")


if __name__ == "__main__":
    app()
