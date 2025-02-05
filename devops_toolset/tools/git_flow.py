""" Helper functions for related Git-Flow tasks automation.
See https://docs.google.com/drawings/d/1orJmg2Eh7iAN5oHvStpyHjeMVn9Zq4wcAE4IXJg_huE/edit """

# ! python
import re
from devops_toolset.tools.constants import dev_branch_regex, release_branch_regex, main_branch_regex


def is_branch_suitable_for_tagging(branch: str) -> bool:
    """ Returns True when branch is suitable for tagging, False if it's not

    Args:
        branch: Branch name to check
    """
    return (
            re.search(dev_branch_regex, branch) is not None
            or re.search(release_branch_regex, branch) is not None
            or re.search(main_branch_regex, branch) is not None
    )


if __name__ == "__main__":
    help(__name__)
