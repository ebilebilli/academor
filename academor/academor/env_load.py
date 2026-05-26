"""Load ``.env`` from known project paths (never commit real secrets)."""
from pathlib import Path

from dotenv import load_dotenv


def load_project_dotenv():
    base_dir = Path(__file__).resolve().parent.parent
    repo_root = base_dir.parent
    docker_env = repo_root / 'docker' / '.env'
    local_env = base_dir / '.env'

    if docker_env.is_file():
        load_dotenv(docker_env, override=False)
    if local_env.is_file():
        load_dotenv(local_env, override=True)
