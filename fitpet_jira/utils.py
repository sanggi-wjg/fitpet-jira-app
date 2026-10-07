import re

from fitpet_jira.config import JiraVersionKey


def escape_issue_id(text: str) -> str:
    """
    PR 이름에서 Jira Issue ID를 추출합니다.

    Example:
        >>> escape_issue_id("[FMP-1234] [ADMIN,CONSUMER] 상품 조회 API 구현")
        "FMP-1234"
    """
    match = re.search(r"\[([A-Z]+-\d+)]", text)
    if match:
        return match.group(1)

    return ""


def escape_version_key(text: str) -> list[JiraVersionKey]:
    """
    PR 이름에서 Version Key 목록을 추출합니다.

    Example:
        >>> escape_version_key("[FMP-1234] [ADMIN,CONSUMER] 상품 조회 API 구현")
        ["ADMIN", "CONSUMER"]
    """
    match = re.search(r"\[([A-Z,\s]+)]", text)
    if match:
        roles = [role.strip() for role in match.group(1).split(",")]
        return [JiraVersionKey(role) for role in roles if role in JiraVersionKey]

    return []
