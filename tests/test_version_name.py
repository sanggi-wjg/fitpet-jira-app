import pytest

from fitpet_jira.util.version_name import bump_patch_version


class TestVersionName:
    @pytest.mark.parametrize(
        "version_name, expected",
        [
            ("BE-MALL-LEGACY-3.13.6", "BE-MALL-LEGACY-3.13.7"),
            ("BE-MALL-ADMIN-1.0.0", "BE-MALL-ADMIN-1.0.1"),
            ("BE-MALL-LEGACY-3.13.9", "BE-MALL-LEGACY-3.13.10"),
            ("BE-MALL-LEGACY-3.13.99", "BE-MALL-LEGACY-3.13.100"),
        ],
    )
    def test_bump_patch_version(self, version_name, expected):
        assert bump_patch_version(version_name) == expected

    @pytest.mark.parametrize(
        "version_name",
        [
            "BE-MALL-LEGACY",
            "BE-MALL-LEGACY-3.13",
            "BE-MALL-LEGACY-3.13.6-hotfix",
            "3.13.6",
        ],
    )
    def test_bump_patch_version_invalid(self, version_name):
        with pytest.raises(ValueError):
            bump_patch_version(version_name)
