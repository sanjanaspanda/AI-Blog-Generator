# import os
# import random
# import subprocess
# from datetime import datetime, timedelta

# def get_positive_int(prompt, default=20):
#     while True:
#         try:
#             user_input = input(f"{prompt} (default {default}): ")
#             if not user_input.strip():
#                 return default
#             value = int(user_input)
#             if value > 0:
#                 return value
#             else:
#                 print("Please enter a positive integer.")
#         except ValueError:
#             print("Invalid input. Please enter a valid integer.")

# def get_repo_path(prompt, default="."):
#     while True:
#         user_input = input(f"{prompt} (default current directory): ")
#         if not user_input.strip():
#             return default
#         if os.path.isdir(user_input):
#             return user_input
#         else:
#             print("Directory does not exist. Please enter a valid path.")

# def get_filename(prompt, default="data.txt"):
#     user_input = input(f"{prompt} (default {default}): ")
#     if not user_input.strip():
#         return default
#     return user_input

# def random_date_in_last_year():
#     today = datetime.now()
#     start_date = today - timedelta(days=365)
#     random_days = random.randint(0, 364)
#     random_seconds = random.randint(0, 23*3600 + 3599)
#     commit_date = start_date + timedelta(days=random_days, seconds=random_seconds)
#     return commit_date

# def make_commit(date, repo_path, filename, message="graph-greener!"):
#     filepath = os.path.join(repo_path, filename)
#     with open(filepath, "a") as f:
#         f.write(f"Commit at {date.isoformat()}\n")
#     subprocess.run(["git", "add", filename], cwd=repo_path)
#     env = os.environ.copy()
#     date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
#     env["GIT_AUTHOR_DATE"] = date_str
#     env["GIT_COMMITTER_DATE"] = date_str
#     subprocess.run(["git", "commit", "-m", message], cwd=repo_path, env=env)

# def main():
#     print("="*60)
#     print("🌱 Welcome to graph-greener - GitHub Contribution Graph Commit Generator 🌱")
#     print("="*60)
#     print("This tool will help you fill your GitHub contribution graph with custom commits.\n")

#     num_commits = get_positive_int("How many commits do you want to make", 20)
#     repo_path = get_repo_path("Enter the path to your local git repository", ".")
#     filename = get_filename("Enter the filename to modify for commits", "data.txt")

#     print(f"\nMaking {num_commits} commits in repo: {repo_path}\nModifying file: {filename}\n")

#     for i in range(num_commits):
#         commit_date = random_date_in_last_year()
#         print(f"[{i+1}/{num_commits}] Committing at {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
#         make_commit(commit_date, repo_path, filename)

#     print("\nPushing commits to your remote repository...")
#     subprocess.run(["git", "push"], cwd=repo_path)
#     print("✅ All done! Check your GitHub contribution graph in a few minutes.\n")
#     print("Tip: Use a dedicated repository for best results. Happy coding!")

# if __name__ == "__main__":
#     main()

import os
import random
import subprocess
from datetime import datetime, timedelta
import math


def get_positive_int(prompt, default=20):
    while True:
        try:
            user_input = input(f"{prompt} (default {default}): ")
            if not user_input.strip():
                return default
            value = int(user_input)
            if value > 0:
                return value
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")


def get_repo_path(prompt, default="."):
    while True:
        user_input = input(f"{prompt} (default current directory): ")
        if not user_input.strip():
            return default
        if os.path.isdir(user_input):
            return user_input
        else:
            print("Directory does not exist. Please enter a valid path.")


def get_date_input(prompt):
    while True:
        try:
            user_input = input(f"{prompt} (format: YYYY-MM-DD): ")
            return datetime.strptime(user_input, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD format.")


def get_commit_message(prompt, default="Update project files"):
    user_input = input(f"{prompt} (default: {default}): ")
    if not user_input.strip():
        return default
    return user_input


def random_date_in_range(start_date, end_date):
    """Generate a random datetime between start_date and end_date"""
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randint(0, days_between)
    random_seconds = random.randint(0, 23*3600 + 3599)
    commit_date = start_date + \
        timedelta(days=random_days, seconds=random_seconds)
    return commit_date


def get_git_status_files(repo_path):
    """Get all files that can be staged from git status"""
    try:
        # Get untracked files
        result_untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        # Get modified files
        result_modified = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        # Get staged files (in case there are any)
        result_staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        all_files = []

        if result_untracked.stdout.strip():
            all_files.extend(result_untracked.stdout.strip().split('\n'))

        if result_modified.stdout.strip():
            all_files.extend(result_modified.stdout.strip().split('\n'))

        if result_staged.stdout.strip():
            all_files.extend(result_staged.stdout.strip().split('\n'))

        # Remove duplicates and empty strings
        all_files = list(set(filter(None, all_files)))

        return all_files
    except subprocess.CalledProcessError:
        return []


def divide_files_into_sections(files, num_sections=4):
    """Divide files into specified number of sections"""
    if not files:
        return []

    files_per_section = math.ceil(len(files) / num_sections)
    sections = []

    for i in range(0, len(files), files_per_section):
        section = files[i:i + files_per_section]
        sections.append(section)

    return sections


def make_commit_with_files(date, repo_path, files, message, section_num=None):
    """Make a commit with specific files at a specific date"""
    if not files:
        print("No files to commit in this section.")
        return False

    # Add files to staging
    for file in files:
        subprocess.run(["git", "add", file], cwd=repo_path)

    # Set up environment for commit date
    env = os.environ.copy()
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    # Create commit message
    if section_num is not None:
        commit_message = f"{message} (Section {section_num})"
    else:
        commit_message = message

    # Make commit
    result = subprocess.run(
        ["git", "commit", "-m", commit_message], cwd=repo_path, env=env)

    return result.returncode == 0


def main():
    print("="*60)
    print("🌱 Welcome to graph-greener - GitHub Contribution Graph Commit Generator 🌱")
    print("="*60)
    print("This tool will help you fill your GitHub contribution graph with custom commits.\n")

    # Get user inputs
    num_commits = get_positive_int("How many commits do you want to make", 20)
    repo_path = get_repo_path(
        "Enter the path to your local git repository", ".")

    # Get date range
    print("\nEnter the date range for commits:")
    start_date = get_date_input("Start date")
    end_date = get_date_input("End date")

    # Validate date range
    if start_date > end_date:
        print("Error: Start date must be before end date.")
        return

    # Get commit message
    commit_message = get_commit_message(
        "Enter commit message", "Update project files")

    # Check if we're in a git repository
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print("Error: The specified path is not a git repository.")
        return

    # Get files from git status
    print("\nChecking git status for files...")
    available_files = get_git_status_files(repo_path)

    if not available_files:
        print("No files found in git status (untracked, modified, or staged).")
        print("Please make some changes to your files first.")
        return

    print(f"Found {len(available_files)} files to work with:")
    for i, file in enumerate(available_files, 1):
        print(f"  {i}. {file}")

    # Divide files into sections
    file_sections = divide_files_into_sections(available_files)

    print(f"\nFiles divided into {len(file_sections)} sections:")
    for i, section in enumerate(file_sections, 1):
        print(f"  Section {i}: {len(section)} files")

    print(
        f"\nMaking {num_commits} commits between {start_date.strftime('%Y-%m-%d')} and {end_date.strftime('%Y-%m-%d')}")
    print(f"Repository: {repo_path}")
    print(f"Commit message base: {commit_message}\n")

    # Make commits
    successful_commits = 0
    commits_per_section = math.ceil(num_commits / len(file_sections))

    for commit_num in range(num_commits):
        # Determine which section to use (cycle through sections)
        section_index = commit_num % len(file_sections)
        current_section = file_sections[section_index]

        # Generate random date in range
        commit_date = random_date_in_range(start_date, end_date)

        print(f"[{commit_num+1}/{num_commits}] Committing section {section_index+1} at {commit_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Files in this commit: {', '.join(current_section)}")

        # Make commit
        if make_commit_with_files(commit_date, repo_path, current_section, commit_message, section_index+1):
            successful_commits += 1
            print(f"  ✅ Commit successful")
        else:
            print(f"  ❌ Commit failed")

        print()

    print(f"Successfully made {successful_commits}/{num_commits} commits.")

    # Ask if user wants to push
    push_choice = input(
        "Do you want to push commits to remote repository? (y/n): ").lower()
    if push_choice in ['y', 'yes']:
        print("Pushing commits to remote repository...")
        result = subprocess.run(["git", "push"], cwd=repo_path)
        if result.returncode == 0:
            print("✅ Push successful!")
        else:
            print("❌ Push failed. You may need to push manually.")

    print("\n✅ All done! Check your GitHub contribution graph in a few minutes.")
    print("Tip: Use a dedicated repository for best results. Happy coding!")


if __name__ == "__main__":
    main()

