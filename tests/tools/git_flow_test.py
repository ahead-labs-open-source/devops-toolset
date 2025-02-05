"""Unit tests for the tools/git_flow module"""

import pytest
import devops_toolset as sut


# region is_branch_suitable_for_tagging()


@pytest.mark.parametrize("branch, expected", [
    ("dev", True),
    ("refs/heads/main", True),
    ("refs/heads/development", True),
    ("refs/heads/feature/my-feature", False),
    ("refs/heads/release/v1.0.0", True)])
def test_is_branch_suitable_for_tagging(branch, expected):
    """Given a branch name, returns True when suitable to tag, False in other case"""

    # Arrange

    # Act
    result: bool = sut.is_branch_suitable_for_tagging(branch)

    # Assert
    assert result == expected


# endregion is_branch_suitable_for_tagging()
