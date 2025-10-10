# pipeline.py

from .core import Bower

def run_pipeline(project_dir: str, model_name: str = None):
    """
    Runs the full Bowerbird pipeline.
    """
    revamp = Bower(project_dir, model_name)
    return revamp.run()
