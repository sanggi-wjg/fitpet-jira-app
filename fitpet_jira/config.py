import enum
from dataclasses import dataclass, field
from typing import Literal

JIRA_VERSION_KEYS_ALLOWED = ["API", "ADMIN", "SELLER", "CONSUMER", "BATCH", "LEGACY"]
JIRA_VERSION_KEY_TYPE = Literal["API", "ADMIN", "SELLER", "CONSUMER", "BATCH", "LEGACY"]


class Command(enum.Enum):
    ASSIGN_VERSION = "assign_version"


@dataclass(frozen=True, slots=True, init=True)
class JiraConfig:
    jira_server: str = field(metadata={"help": "Jira server (domain url)"})
    jira_project: str = field(metadata={"help": "Jira project"})
    jira_username: str = field(metadata={"help": "Jira username"})
    jira_token: str = field(metadata={"help": "Jira token"})


@dataclass(frozen=True, slots=True, init=True)
class CommandReqeust:
    command: Command = field(metadata={"help": "실행 명령어"})
    pr_name: str = field(
        metadata={"help": "Github PR 이름 (예시, [FMP-1234] [ADMIN,CONSUMER] 상품 조회 API 구현) "},
    )
    jira_issue_id: str = field(
        metadata={"help": "PR 이름으로 issue_id 를 찾습니다. (예시 pr_name 경우, FMP-1234 입니다) "},
    )
    jira_version_key: list[JIRA_VERSION_KEY_TYPE] = field(
        metadata={"help": "PR 이름으로 version_key 를 찾습니다. (예시 pr_name 경우, ADMIN,CONSUMER 입니다) "},
    )

    def is_ready_to_go(self) -> bool:
        return self.jira_issue_id and self.jira_version_key and len(self.jira_version_key) > 0
