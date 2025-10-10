# cli.py

import argparse
from .pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Bowerbirds - AI Project Revamper")
    parser.add_argument("project_dir", help="Path to the project directory")
    parser.add_argument("--model", dest="model_name", default=None, help="Model name for LiteLLM (optional)")

    args = parser.parse_args()
    result = run_pipeline(args.project_dir, args.model_name)
    print(result)

if __name__ == "__main__":
    main()
