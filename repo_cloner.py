import os
import shutil
import logging
from git import Repo

def clone_repo(repo_url, clone_dir="cloned_repo"):
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)
    try:
        Repo.clone_from(repo_url, clone_dir)
        logging.info(f"Cloned repo to {clone_dir}")
        return os.path.abspath(clone_dir)
    except Exception as e:
        logging.error(f"Failed to clone repo: {e}")
        raise
