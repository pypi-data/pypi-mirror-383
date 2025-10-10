# core.py

import os

from bowerbirds.config import SYSTEM_PROMPT
from .summary import *
from .full_meta import *
from .lite_llm import run_litellm

class Bower:
    def __init__(self, project_dir: str, model_name: str = None):
        self.project_dir = project_dir
        self.model_name = model_name

    def run(self):
        # Step 1: Process the directory
        combined_meta_path = process_directory_combined_json(self.project_dir)

        # Step 2: Enrich metadata
        full_meta_path = pipe_meta(self.project_dir,combined_meta_path,"full_metadata.json")

        predefined_prompt = SYSTEM_PROMPT

        # Step 3: Based on model_name
        if self.model_name is None:
            print(
                "Your project metadata has been created. "
                "Put 'full_metadata.json' into any model manually "
                f"along with this prompt: '{predefined_prompt}'"
            )
            return full_meta_path

        else:
            # Load JSON text for model
            with open(full_meta_path, "r") as f:
                json_text = f.read()

            output = run_litellm(predefined_prompt, json_text, model_name=self.model_name)
            print("Successfully revamped your project.")
            return output
