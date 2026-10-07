from pydantic import BaseModel, ConfigDict, Field, SecretStr


class JiraConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    server: str = Field(description="Jira 서버 주소 (예시, https://xxx.atlassian.net)")
    token: SecretStr = Field(description="Jira API 토큰")
    project: str = Field(description="Jira 프로젝트 키 (예시, FMP)")
    username: SecretStr = Field(description="Jira 계정 이메일")
