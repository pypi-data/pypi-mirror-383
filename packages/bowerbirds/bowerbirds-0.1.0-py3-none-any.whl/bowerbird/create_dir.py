import os
import json

def create_ai_project_structure(project_name: str):
    # Final folder structure
    folders = [
        "docker",
        "assets",
        "data/raw",
        "docs",
        "data/processed",
        "data/samples",
        "notebooks",
        f"src/{project_name.lower()}/utils",
        f"src/{project_name.lower()}/model",
        "scripts",
        "outputs",
        "unidentified_files"
    ]

    files = [
        "LICENSE",
        "README.md",
        "CHANGELOG.md",
        "pyproject.toml",
        "requirements.txt",
        ".gitignore",
        ".gitattributes"
    ]

    # Descriptive metadata for each folder
    folder_metadata = {
        "docker": "Contains Dockerfile and docker-compose.yml for containerization and reproducible environments.",
        "assets": "Holds images, diagrams, GIFs, logos, and other visual assets for README or documentation.",
        "data/raw": "Original, immutable datasets used for training or evaluation. Should not be modified.",
        "data/processed": "Preprocessed datasets ready to be used for training models.",
        "data/samples": "Small example datasets used for demos, testing, or quick experiments.",
        "docs": "Documentation files, including architecture diagrams, API references, and troubleshooting guides.",
        "notebooks": "Jupyter notebooks for exploratory data analysis, prototyping, and experimentation.",
        f"src/{project_name.lower()}/utils": "Python utility scripts and helper functions for data processing, training, or inference.",
        f"src/{project_name.lower()}/model": "Python code defining model architectures, layers, training loops, and evaluation logic.",
        "scripts": "Shell or Python scripts for automating training, evaluation, exporting models, or running experiments.",
        "outputs": "Directory to store experiment results, model checkpoints, logs, metrics, and inference outputs.",
        "unidentified_files": "A catch-all folder for miscellaneous or temporary files that don’t belong elsewhere."
    }

    # Create folders
    for folder in folders:
        path = os.path.join(project_name, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Created folder: {path}")

    # Create empty files
    for file in files:
        path = os.path.join(project_name, file)
        with open(path, 'w') as f:
            f.write("")  # empty file
        print(f"Created file: {path}")

    # Create metadata JSON
    metadata_path = os.path.join(project_name, "structure_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(folder_metadata, f, indent=4)

    print(f"\nProject '{project_name}' scaffold and metadata.json with descriptive info created successfully!")

# Example usage
if __name__ == "__main__":
    project_name = input("Enter the AI project name: ").strip()
    create_ai_project_structure(project_name)
