from pydantic import BaseModel, ConfigDict, Field


class JiraConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    jira_server: str = Field(description="Jira 서버 주소 (예시, https://xxx.atlassian.net)")
    jira_token: str = Field(description="Jira API 토큰")
    jira_project: str = Field(description="Jira 프로젝트 키 (예시, FMP)")
    jira_username: str = Field(description="Jira 계정 이메일")

    def __repr__(self) -> str:
        return f"JiraConfig(jira_server={self.jira_server}, jira_token=***, jira_project={self.jira_project}, jira_username=${self.jira_username[:5]})"
