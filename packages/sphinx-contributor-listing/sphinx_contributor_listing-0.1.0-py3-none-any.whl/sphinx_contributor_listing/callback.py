# This file is part of sphinx-contributor-listing.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 3, as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Contains the callback functions for the sphinx-contributor-listing extension."""

from pathlib import Path
from typing import Any

from docutils import nodes
from git import InvalidGitRepositoryError, Repo
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


def add_contributor_context(
    _app: Sphinx,
    _pagename: str,
    _templatename: str,
    context: dict[str, Any],
    _doctree: nodes.document | None,
) -> None:
    """Add contributor information to the page context."""

    def get_contributors_for_file(
        pagename: str, page_source_suffix: str
    ) -> list[tuple[str, str]]:
        """Get contributors for a specific file."""
        if (
            "display_contributors" not in context
            or "github_folder" not in context
            or "github_url" not in context
        ):
            return []

        if context["display_contributors"]:
            filename = f"{pagename}{page_source_suffix}"
            paths = context["github_folder"][1:] + filename

            try:
                repo = Repo(".")
            except InvalidGitRepositoryError:
                cwd = str(Path.cwd())
                ghfolder = context["github_folder"][:-1]
                if ghfolder and cwd.endswith(ghfolder):
                    try:
                        repo = Repo(cwd.rpartition(ghfolder)[0])
                    except InvalidGitRepositoryError:
                        logger.warning("The local Git repository could not be found.")
                        return []
                else:
                    logger.warning("The local Git repository could not be found.")
                    return []

            since: str | None = None

            if (
                "display_contributors_since" in context
                and context["display_contributors_since"]
                and context["display_contributors_since"].strip()
            ):
                since = context["display_contributors_since"]

            try:
                commits = repo.iter_commits(paths=paths, since=since)
            except ValueError as e:
                logger.warning("Failed to iterate through the Git commits: %s", str(e))
                return []

            contributors_dict: dict[str, dict[str, Any]] = {}
            for commit in commits:
                contributors = [commit.author.name]
                contributors.extend(co_author.name for co_author in commit.co_authors)
                for contributor in contributors:
                    if contributor is None:
                        continue
                    if (
                        contributor not in contributors_dict
                        or commit.committed_date
                        > contributors_dict[contributor]["date"]
                    ):
                        contributors_dict[contributor] = {
                            "date": commit.committed_date,
                            "sha": commit.hexsha,
                        }
            # github_page contains the link to the contributor's latest commit
            contributors_list = [
                (name, f"{context['github_url']}/commit/{data['sha']}")
                for name, data in contributors_dict.items()
            ]

            return sorted(contributors_list)

        return []

    context["get_contributors_for_file"] = get_contributors_for_file
