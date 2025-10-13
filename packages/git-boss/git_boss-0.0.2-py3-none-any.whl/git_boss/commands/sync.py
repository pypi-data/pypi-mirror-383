from typing import Optional

from git_boss.config import Config


def run(cfg: Optional[Config] = None) -> int:
    """Run the sync command. Currently a stub that prints Hello!"""
    print("Hello!")
    return 0
