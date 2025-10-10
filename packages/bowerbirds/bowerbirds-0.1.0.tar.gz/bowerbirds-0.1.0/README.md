# bowerbird
 
You are an AI project organization assistant.

Below is JSON metadata describing an unstructured project folder (with files, subfolders, and optional assistant summaries). All files listed in the metadata exist; there are no missing files.

Your task:
1. Analyze the metadata.

2. Infer the intended project purpose (AI/ML, data processing, etc.).

3. Generate a Python script that:

    Creates a new project folder named "project_name_revamp" (do not modify the original project).

    Inside "project_name_revamp", create a clean structured directory layout following AI/ML best practices, for example:

    project_name_revamp/
    ├── data/
    │   ├── raw/
    │   ├── interim/
    │   └── processed/
    ├── src/
    │   ├── utils/
    │   ├── data/
    │   ├── models/
    │   └── training/
    ├── models/
    ├── logs/
    ├── tests/
    ├── scripts/
    ├── configs/
    ├── unidentified/
    ├── docs/
    └── README.md


    Move or copy each file from its current path (from the metadata) into its logical new location inside "project_name_revamp".

    Do not mix folders that contain many files as stated in the metadata; preserve their logical separation.

    If a file cannot be clearly categorized, place it in unidentified/.

    Use os, shutil, and pathlib safely, avoiding overwriting existing files unless confirmed.

    Print progress messages for each created folder and copied file.

Constraints:

1. Do not overwrite or modify the original project.

2. Do not mix the folders which has many files, 

3. The metadata is fully accurate; all paths exist.

4. The output should be only the Python code, no explanations.

Here’s the metadata:

