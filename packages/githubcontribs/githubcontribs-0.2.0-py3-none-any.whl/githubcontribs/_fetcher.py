import os
import warnings
from datetime import datetime, timedelta

import pandas as pd
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

warnings.filterwarnings("ignore")
urllib3.disable_warnings()
from dotenv import load_dotenv


class Fetcher:
    """Fetch GitHub contributions (commits, issues, PRs) for a given organization.

    Usage::

        fetcher = Fetcher(org_name="my-org")
        df = contribs.run()
    """

    def __init__(self, org_name: str, token: str = None):
        """Init.

        Args:
            org_name: Name of the GitHub organization.
            token: GitHub personal access token. Read from `GITHUB_TOKEN` env var if `None`. Loads `.env` from the current working directory.
        """
        load_dotenv()
        token = token or os.getenv("GITHUB_TOKEN")
        if token is None:
            raise ValueError(
                "No GitHub token provided. Set env variable `GITHUB_TOKEN`, e.g. in `.env` in the current working directory."
            )

        self.org_name = org_name
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = "https://api.github.com"

        # Configure retry strategy
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        # Create session with retry strategy
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.headers.update(self.headers)

    def _fetch_contribs_as_dicts(
        self, repo_name: str, start_date: str | datetime | None = None
    ) -> tuple[list[dict], list[dict], list[dict]]:
        """Get commits, issues, and PRs for a specific repository since start_date as dicts."""
        if isinstance(start_date, str):
            start_date_dt = datetime.fromisoformat(start_date)
        elif start_date is None:
            start_date_dt = datetime.now() - timedelta(days=90)
        else:
            start_date_dt = start_date

        print(
            f"fetching contributions for repository {repo_name} since {start_date_dt:%Y-%m-%d}"
        )

        start_date_str: str = start_date_dt.isoformat()

        def paginate_results(endpoint: str) -> list[dict]:
            results = []
            page: int = 1
            while True:
                params = {
                    "state": "all",
                    "page": page,
                    "per_page": 100,
                    "since": start_date_str,  # For commits: filters by author date; for issues/PRs: filters by updated_at
                }

                response = self.session.get(
                    f"{self.base_url}/repos/{self.org_name}/{repo_name}/{endpoint}",
                    params=params,  # type: ignore
                )
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                results.extend(data)
                page += 1
            return results

        commits = paginate_results("commits")
        issues = paginate_results("issues")
        prs = [issue for issue in issues if "pull_request" in issue]
        issues = [issue for issue in issues if "pull_request" not in issue]

        print(f"found {len(commits)} commits, {len(issues)} issues, and {len(prs)} PRs")

        return commits, issues, prs

    def _fetch_contribs_per_repo(
        self, repo_name: str, start_date: str | None = None
    ) -> pd.DataFrame:
        """Get commits, issues, and PRs for a specific repository since start_date as dataframes."""
        commits, issues, prs = self._fetch_contribs_as_dicts(repo_name, start_date)

        # Convert start_date for filtering issues and PRs
        if isinstance(start_date, str):
            start_date_dt = datetime.fromisoformat(start_date)
        elif start_date is None:
            start_date_dt = datetime.now() - timedelta(days=90)
        else:
            start_date_dt = start_date

        data = []

        for commit in commits:
            commit_date = commit["commit"]["author"]["date"][:10]
            data.append(
                {
                    "date": commit_date,
                    "author": (
                        commit.get("author", {}).get("login")
                        or commit.get("commit", {}).get("author", {}).get("name")
                        or "unknown"
                    ),
                    "repo": repo_name,
                    "type": "commit",
                    "title": commit["commit"]["message"],
                }
            )

        for issue in issues:
            created_date = issue["created_at"][:10]
            # Filter by date - skip if created before start_date
            if datetime.fromisoformat(created_date) < start_date_dt:
                continue
            data.append(
                {
                    "date": created_date,
                    "author": issue["user"]["login"],
                    "repo": repo_name,
                    "type": "issue",
                    "title": issue["title"],
                    "state": issue["state"],
                    "number": issue["number"],
                }
            )

        for pr in prs:
            created_date = pr["created_at"][:10]
            # Filter by date - skip if created before start_date
            if datetime.fromisoformat(created_date) < start_date_dt:
                continue
            data.append(
                {
                    "date": created_date,
                    "author": pr["user"]["login"],
                    "repo": repo_name,
                    "type": "pr",
                    "title": pr["title"],
                    "state": pr["state"],
                    "number": pr["number"],
                }
            )

        return pd.DataFrame(data)

    def run(
        self, repo_names: str | list[str], *, start_date: str | None = None
    ) -> pd.DataFrame:
        """Get commits, issues, and PRs for all or specific repositories since start_date as a dataframe.

        Args:
            repo_names: List of repository names. If None, fetches all repositories in the organization.
            start_date: Start date in ISO format (YYYY-MM-DD). Defaults to 90 days ago if None.
        """
        if isinstance(repo_names, str):
            repo_names = [repo_names]

        contribs = pd.DataFrame()
        for repo_name in repo_names:
            repo_contribs = self._fetch_contribs_per_repo(repo_name, start_date)
            contribs = pd.concat([contribs, repo_contribs], ignore_index=True)

        return contribs
