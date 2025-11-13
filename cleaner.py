import os
import shutil
from pathlib import Path

# folders we want to REMOVE entirely inside each repo
JUNK_DIRS = {
    ".git", "node_modules", "venv", "dist", "build",
    "coverage", ".idea", ".vscode"
}

# file patterns / extensions we want to delete
JUNK_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".pdf",
    ".zip"
}

# special single-file patterns to delete
JUNK_SUFFIXES = (
    ".min.js",  # minified bundles
    ".lock",    # package-lock.json, pnpm-lock.yaml, etc.
)

# things we always keep even if they don't look like code
ALWAYS_KEEP_FILENAMES = {
    "requirements.txt",
    "package.json",
    "pyproject.toml",
}

CODE_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".php", ".vue",
    ".html", ".css", ".scss", ".sass", ".less",
    ".sql", ".c", ".cpp", ".h", ".hpp", ".java",
    ".rb", ".go", ".rs", ".swift", ".kt", ".cs",
    ".sh", ".bat", ".xml", ".yaml", ".yml",
    ".ini", ".cfg", ".toml"
}

TEXT_EXTS = {
    ".md", ".txt", ".rst"
}

# folders we KEEP fully if they exist
KEEP_DIR_PREFIXES = ("src", "app", "lib", "docs")


def copy_repos_to_cleaned(parent_folder: str, cleaned_root: str):
    os.makedirs(cleaned_root, exist_ok=True)

    repos = [
        d for d in os.listdir(parent_folder)
        if os.path.isdir(os.path.join(parent_folder, d))
        and not d.startswith(".")
        and d != os.path.basename(cleaned_root)
    ]

    if not repos:
        print("No repositories found.")
        return []

    copied_paths = []
    for repo in repos:
        src = os.path.join(parent_folder, repo)
        dst = os.path.join(cleaned_root, repo)

        # if already exists, remove to get a fresh copy
        if os.path.exists(dst):
            shutil.rmtree(dst)

        shutil.copytree(src, dst)
        copied_paths.append(dst)
        print(f"Copied {repo} -> {dst}")

    return copied_paths


def is_large_ipynb(path: str, max_mb=5):
    if not path.endswith(".ipynb"):
        return False
    size_mb = os.path.getsize(path) / (1024 * 1024)
    return size_mb > max_mb


def should_delete_file(path: str):
    name = os.path.basename(path)
    lower = name.lower()
    ext = os.path.splitext(name)[1].lower()

    # delete .gitignore
    if name == ".gitignore":
        return True

    # keep some important files
    if name in ALWAYS_KEEP_FILENAMES:
        return False
    if lower.startswith("readme") and lower.endswith(".md"):
        return False

    # images, pdf, zip
    if ext in JUNK_EXTS:
        return True

    # .min.js, .lock
    for s in JUNK_SUFFIXES:
        if lower.endswith(s):
            return True

    # big ipynb
    if is_large_ipynb(path):
        return True

    return False


def delete_junk_dirs(repo_root: str):
    # walk top-down so we can modify dirs in-place
    for root, dirs, files in os.walk(repo_root, topdown=True):
        # remove junk dirs from this level
        dirs_to_remove = [d for d in dirs if d in JUNK_DIRS]
        for d in dirs_to_remove:
            full = os.path.join(root, d)
            shutil.rmtree(full, ignore_errors=True)
            dirs.remove(d)  # so os.walk won't go into it


def classify_and_move_files(repo_root: str):
    """
    After we deleted junk, walk the repo and move files into:
        repo_root/code/... and repo_root/text/...
    preserving relative paths.
    """
    code_root = os.path.join(repo_root, "code")
    text_root = os.path.join(repo_root, "text")
    os.makedirs(code_root, exist_ok=True)
    os.makedirs(text_root, exist_ok=True)

    # we will collect empty dirs to remove later
    all_files = []

    for root, dirs, files in os.walk(repo_root, topdown=True):
        # don't recurse into code/ and text/ again
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in (code_root, text_root)]

        for f in files:
            src_path = os.path.join(root, f)

            # skip if it's already inside code/ or text/
            if src_path.startswith(code_root) or src_path.startswith(text_root):
                continue

            # if it's junk, we should have removed it earlier, but double-check
            if should_delete_file(src_path):
                os.remove(src_path)
                continue

            rel = os.path.relpath(src_path, repo_root)
            ext = Path(f).suffix.lower()

            # text priority: README, docs/*.md
            if f.lower().startswith("readme") and ext == ".md":
                dest_base = text_root
            elif rel.split(os.sep)[0] == "docs" and ext == ".md":
                dest_base = text_root
            elif ext in TEXT_EXTS:
                dest_base = text_root
            else:
                # code or config
                if ext in CODE_EXTS or rel.split(os.sep)[0] in ("src", "app", "lib"):
                    dest_base = code_root
                else:
                    # unknown -> toss to text to be safe
                    dest_base = text_root

            dest_path = os.path.join(dest_base, rel)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.move(src_path, dest_path)

            all_files.append(dest_path)

    # now remove empty dirs (except code/ and text/)
    for root, dirs, files in os.walk(repo_root, topdown=False):
        if root in (code_root, text_root):
            continue
        if not os.listdir(root):
            try:
                os.rmdir(root)
            except OSError:
                pass


def clean_single_repo(repo_root: str):
    # 1. remove trash dirs like .git, node_modules, ...
    delete_junk_dirs(repo_root)

    # 2. delete trash files anywhere
    for root, dirs, files in os.walk(repo_root):
        for f in files:
            path = os.path.join(root, f)
            if should_delete_file(path):
                os.remove(path)

    # 3. separate into code/ and text/
    classify_and_move_files(repo_root)
    print(f"Cleaned {repo_root}")


def main():
    parent_folder = input("Enter path to folder containing repos: ").strip()
    if not parent_folder:
        print("No folder provided.")
        return

    cleaned_root = os.path.join(parent_folder, "cleaned-repo")
    copied = copy_repos_to_cleaned(parent_folder, cleaned_root)

    if not copied:
        return

    print("\n=== CLEANING COPIED REPOS ===")
    for repo_path in copied:
        clean_single_repo(repo_path)

    print("\nAll done. Check the 'cleaned-repo' folder.")


if __name__ == "__main__":
    main()