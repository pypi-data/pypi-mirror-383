from packaging.version import Version

from scripts.get_version import get_version


def has_version_bumped(
    latest_git_tag: str,
) -> bool:
    """
    Make sure version has been bumped.

    :param latest_git_tag: Latest tag from Git.
    :type latest_git_tag: str
    :return: True if the current version of the project is higher than the latest Git tag.
    :rtype: bool
    """
    current_version = get_version()
    latest_version = Version(latest_git_tag.lstrip("v"))
    return current_version > latest_version


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:  # noqa: PLR2004 - magic-value-comparison
        print("Usage: python compare_tags.py <latest_git_tag>")
        sys.exit(1)

    latest_git_tag = sys.argv[1]

    if has_version_bumped(latest_git_tag):
        print(f"Version has been bumped since the latest tag {latest_git_tag}.")
        sys.exit(0)
    else:
        print(f"Version has NOT been bumped since the latest tag {latest_git_tag}.")
        sys.exit(1)
