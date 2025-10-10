import os
import json
import re
from collections import defaultdict, Counter
from .config import *

# Configuration

METADATA1_FILE = "m2.json"  # <-- path to your assistant summaries


def normalize_filename(name):
    """Replace digits with a placeholder to detect common patterns."""
    base, ext = os.path.splitext(name)
    normalized = re.sub(r'\d+', '_', base)
    return normalized

def longest_common_substring(strs):
    """Find the longest common substring among a list of strings."""
    if not strs:
        return ""
    shortest = min(strs, key=len)
    length = len(shortest)
    for l in range(length, 0, -1):
        for i in range(length - l + 1):
            substr = shortest[i:i+l]
            if all(substr in s for s in strs):
                return substr
    return ""
    
def natural_sort_key(s):
    """Sorts strings with numbers in natural order (e.g., file2 before file10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]


def get_folder_metadata(folder_path):
    folder_data = {}

    for root, dirs, files in os.walk(folder_path):
        rel_root = os.path.relpath(root, folder_path)
        if rel_root == ".":
            rel_root = ""

        if len(files) > FILE_COUNT_THRESHOLD:
            # Summarize folder
            extensions = [os.path.splitext(f)[1] for f in files]
            ext_count = dict(Counter(extensions))

            # Group files by extension
            files_by_ext = defaultdict(list)
            for f in files:
                ext = os.path.splitext(f)[1]
                files_by_ext[ext].append(f)

            common_names = {}
            for ext, file_list in files_by_ext.items():
                normalized_files = [normalize_filename(f) for f in file_list]
                lcs = longest_common_substring(normalized_files)
                if lcs and len(lcs) > 1:
                    common_names[ext] = lcs
                else:
                    sorted_files = sorted(file_list, key=natural_sort_key)
                    common_names[ext] = sorted_files[:SAMPLE_FILE_COUNT]
                    # common_names[ext] = file_list[:SAMPLE_FILE_COUNT]

            folder_data[rel_root] = {
                "folder": root,
                "num_files": len(files),
                "extensions": ext_count,
                "common_names": common_names
            }
        else:
            folder_data[rel_root] = {
                "folder": root,
                "files": [os.path.join(root, f) for f in files],
                "subfolders": dirs
            }

    return folder_data

def enrich_with_summaries(folder_data, summary_file):
    """Add assistant summaries for all Python files, using a placeholder if missing."""
    # with open(summary_file, "r") as f:
    #     summaries = json.load(f)

    summaries=json.loads(summary_file)
    # Create a lookup dictionary
    summary_lookup = {item["file_path"]: item["assistant_summary"] for item in summaries}

    for folder_info in folder_data.values():
        if "files" in folder_info:
            py_summaries = {}
            for file_path in folder_info["files"]:
                if file_path.endswith(".py"):
                    # Use the summary if available, else placeholder
                    py_summaries[file_path] = summary_lookup.get(file_path, "No assistant summary available")
            if py_summaries:
                folder_info["assistant_summaries"] = py_summaries

    return folder_data


def pipe_meta(project_dir,meta1_file,output):
    metadata = get_folder_metadata(project_dir)
    metadata = enrich_with_summaries(metadata, meta1_file)

    with open(output, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Metadata saved to {output}")
    return output