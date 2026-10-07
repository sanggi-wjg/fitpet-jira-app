from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class JiraVersionKey(StrEnum):
    API = "API"
    ADMIN = "ADMIN"
    SELLER = "SELLER"
    CONSUMER = "CONSUMER"
    BATCH = "BATCH"
    LEGACY = "LEGACY"


class AssignVersionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    pr_name: str = Field(
        description="Github PR 이름 (예시, [FMP-1234] [ADMIN,CONSUMER] 상품 조회 API 구현)",
    )
    jira_issue_id: str = Field(
        description="PR 이름으로 issue_id 를 찾습니다. (예시 pr_name 경우, FMP-1234 입니다) ",
    )
    jira_version_keys: list[JiraVersionKey] = Field(
        description="PR 이름으로 version_key 를 찾습니다. (예시 pr_name 경우, ADMIN,CONSUMER 입니다) ",
    )

    def is_ready_to_go(self) -> bool:
        return all(
            [
                self.jira_issue_id,
                self.jira_version_keys,
                len(self.jira_version_keys) > 0,
            ]
        )
