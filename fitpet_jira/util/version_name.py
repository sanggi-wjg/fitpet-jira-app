import re


def bump_patch_version(version_name: str) -> str:
    """
    릴리즈 버전 이름의 패치 버전을 1 올립니다.

    Example:
        >>> bump_patch_version("BE-MALL-LEGACY-3.13.6")
        "BE-MALL-LEGACY-3.13.7"
    """
    match = re.fullmatch(r"(.+-\d+\.\d+\.)(\d+)", version_name)
    if not match:
        raise ValueError(f"시멘틱 버전 형식의 릴리즈 이름이 아닙니다: {version_name}")

    prefix, patch = match.groups()
    return f"{prefix}{int(patch) + 1}"
