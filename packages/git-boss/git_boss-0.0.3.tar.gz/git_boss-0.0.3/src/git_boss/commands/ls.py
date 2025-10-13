from typing import List

from git_boss.config import Config


def run(cfg: Config, cfg_path: str) -> int:
    projects: List[str] = cfg.gitProjects or []
    if not projects:
        print("No git projects configured")
        return 0

    for p in projects:
        print(p)

    return 0
