from __future__ import annotations

from typing import TYPE_CHECKING

from predibase.resources.repo import Repo

if TYPE_CHECKING:
    from predibase import Predibase


class Repos:
    def __init__(self, client: Predibase):
        self._client = client

    def create(self, *, name: str, description: str | None = None, exists_ok: bool = False) -> Repo:
        """Create a new repository.

        Args:
            name: The name of the repository to create
            description: Optional description for the repository
            exists_ok: If True, do not raise an error if the repository already exists

        Returns:
            Repo: The created repository

        Example:
            >>> pb = Predibase()
            >>> repo = pb.repos.create(name="my-repo", description="My fine-tuned models")
        """
        resp = self._client.http_post(
            "/v2/repos",
            json={
                "name": name,
                "description": description,
                "existsOk": exists_ok,
            },
        )
        return Repo.model_validate(resp)

    def get(self, repo_ref: str | Repo) -> Repo:
        """Get a repository by name or UUID.

        Args:
            repo_ref: The repository name, UUID, or Repo object

        Returns:
            Repo: The repository

        Example:
            >>> pb = Predibase()
            >>> repo = pb.repos.get("my-repo")
        """
        if isinstance(repo_ref, Repo):
            repo_ref = repo_ref.name

        return Repo.model_validate(self._client.http_get(f"/v2/repos/{repo_ref}"))

    def list(self, limit: int = 10) -> list[Repo]:
        """List repositories.

        Args:
            limit: Maximum number of repositories to return (default: 10)

        Returns:
            list[Repo]: List of repositories

        Example:
            >>> pb = Predibase()
            >>> repos = pb.repos.list(limit=20)
        """
        resp = self._client.http_get(f"/v2/repos?limit={limit}")
        return [Repo.model_validate(r) for r in resp["data"]["repos"]]

    def delete(self, repo_ref: str | Repo) -> None:
        """Delete a repository by name or UUID.

        This will permanently delete the repository and all its versions.
        Repositories with active finetuning jobs cannot be deleted.

        Args:
            repo_ref: The repository name, UUID, or Repo object to delete

        Raises:
            HTTPError: If the repository is not found (404), has active finetuning jobs (403),
                      or if deletion fails for any other reason

        Example:
            >>> pb = Predibase()
            >>> pb.repos.delete("my-repo")
            >>> # Or using a Repo object
            >>> repo = pb.repos.get("my-repo")
            >>> pb.repos.delete(repo)
        """
        if isinstance(repo_ref, Repo):
            repo_ref = repo_ref.name

        self._client.http_delete(f"/v2/repos/{repo_ref}")
