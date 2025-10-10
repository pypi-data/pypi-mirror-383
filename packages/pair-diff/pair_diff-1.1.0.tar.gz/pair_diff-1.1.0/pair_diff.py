import os
import sys
import filecmp
import csv
from tabulate import tabulate
from collections import defaultdict

def collect_differences(dir1, dir2, ignore=None, base_path=""):
    """Collect structural differences between two directories"""
    dcmp = filecmp.dircmp(dir1, dir2, ignore=ignore)
    result = {
        'left_only': [],    # Items only in dir1
        'right_only': [],   # Items only in dir2
        'funny_files': [],  # Items with inconsistent types
        'common': [],       # Common items
        'subdirs': {}       # Differences in subdirectories
    }
    
    # Collect differences in current directory
    current_path = base_path if base_path else "."
    
    for item in dcmp.left_only:
        result['left_only'].append(os.path.join(current_path, item))
    
    for item in dcmp.right_only:
        result['right_only'].append(os.path.join(current_path, item))
    
    for item in dcmp.funny_files:
        result['funny_files'].append(os.path.join(current_path, item))
    
    # Collect common items
    for item in dcmp.common:
        result['common'].append(os.path.join(current_path, item))
    
    # Process subdirectories recursively
    for subdir in dcmp.common_dirs:
        sub_path = os.path.join(base_path, subdir) if base_path else subdir
        result['subdirs'][subdir] = collect_differences(
            os.path.join(dir1, subdir),
            os.path.join(dir2, subdir),
            ignore=ignore,
            base_path=sub_path
        )
    
    return result

def print_table(left_items, common_items, right_items, dir1, dir2, title=None):
    """Print items in a three-column table using tabulate"""
    if title:
        print(f"\n\033[1;34m{title}\033[0m")
    
    # Prepare table data, ensuring consistent row count
    max_rows = max(len(left_items), len(common_items), len(right_items))
    table_data = []
    
    for i in range(max_rows):
        left = left_items[i] if i < len(left_items) else ""
        common = common_items[i] if i < len(common_items) else ""
        right = right_items[i] if i < len(right_items) else ""
        
        # Add colors for different types of items
        left_str = f"\033[1;31m{left}\033[0m"
        right_str = f"\033[1;32m{right}\033[0m"
        
        table_data.append([left_str, common, right_str])
    
    # Generate table using tabulate
    headers = [dir1, "Common Items", dir2]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def print_differences(diff_info, dir1, dir2, parent_dir=""):
    """Recursively print collected differences"""
    # Prepare item lists for current directory
    left_items = diff_info['left_only']
    common_items = diff_info['common']
    right_items = diff_info['right_only']
    
    # Print table for current directory
    if parent_dir:
        title = f"Directory: {parent_dir}"
    else:
        title = "Root Directory"
    
    print_table(left_items, common_items, right_items, dir1, dir2, title)
    
    # Print items with inconsistent types
    if diff_info['funny_files']:
        print(f"\n\033[1;33mInconsistent Types (File/Directory Conflicts):\033[0m")
        for item in diff_info['funny_files']:
            print(f"  - {item}")
    
    # Process subdirectories recursively
    for subdir, sub_diff in diff_info['subdirs'].items():
        subdir_path = os.path.join(parent_dir, subdir) if parent_dir else subdir
        print_differences(sub_diff, dir1, dir2, subdir_path)

def export_to_csv(diff_info, dir1, dir2, csv_file, parent_dir=""):
    """Export differences to CSV file"""
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header if file is empty
        if os.path.getsize(csv_file) == 0:
            writer.writerow(["Directory", "Only in " + dir1, "Common Items", "Only in " + dir2, "Type Conflicts"])
        
        # Prepare data for current directory
        directory = parent_dir if parent_dir else "Root"
        left_only = ", ".join(diff_info['left_only']) if diff_info['left_only'] else ""
        common = ", ".join(diff_info['common']) if diff_info['common'] else ""
        right_only = ", ".join(diff_info['right_only']) if diff_info['right_only'] else ""
        funny_files = ", ".join(diff_info['funny_files']) if diff_info['funny_files'] else ""
        
        # Write row for current directory
        writer.writerow([directory, left_only, common, right_only, funny_files])
        
        # Process subdirectories recursively
        for subdir, sub_diff in diff_info['subdirs'].items():
            subdir_path = os.path.join(parent_dir, subdir) if parent_dir else subdir
            export_to_csv(sub_diff, dir1, dir2, csv_file, subdir_path)

def has_differences(diff_info):
    """Check if there are any differences"""
    if diff_info['left_only'] or diff_info['right_only'] or diff_info['funny_files']:
        return True
    
    for sub_diff in diff_info['subdirs'].values():
        if has_differences(sub_diff):
            return True
    
    return False

def main():
    """CLI entry point for pair-diff tool"""
    # check command line arguments
    if len(sys.argv) != 3:
        print(f"\033[1;31mUsage Error!\033[0m Correct usage:")
        print(f"  pair-diff <directory1_path> <directory2_path>")
        print(f"Example:")
        print(f"  pair-diff ./A-dir1 ./B-dir2")
        sys.exit(1)
    
    # get directory paths from command line
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    
    # validate directories exist and are valid
    if not os.path.exists(dir1):
        print(f"\033[1;31mError:\033[0m Directory '{dir1}' does not exist")
        sys.exit(1)
    if not os.path.isdir(dir1):
        print(f"\033[1;31mError:\033[0m '{dir1}' is not a valid directory")
        sys.exit(1)
    if not os.path.exists(dir2):
        print(f"\033[1;31mError:\033[0m Directory '{dir2}' does not exist")
        sys.exit(1)
    if not os.path.isdir(dir2):
        print(f"\033[1;31mError:\033[0m '{dir2}' is not a valid directory")
        sys.exit(1)
    
    # ignore list for common files/directories
    ignore_list = [
        ".git",          # ignore git directory
        "*.log",         # ignore all .log files
        "tmp",           # ignore tmp directory
        "__pycache__"    # ignore Python cache directory
    ]
    
    # start comparison
    print(f"\033[1;34m=== Starting Directory Structure Comparison ===\033[0m")
    diff_info = collect_differences(dir1, dir2, ignore=ignore_list)
    
    # print results
    print_differences(diff_info, dir1, dir2)
    
    # export results to CSV
    csv_filename = f"diff_{os.path.basename(dir1)}_{os.path.basename(dir2)}.csv"
    # Create empty file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        pass
    
    # Export differences to CSV
    export_to_csv(diff_info, dir1, dir2, csv_filename)
    print(f"\n\033[1;34mDifferences exported to {csv_filename}\033[0m")
    
    # final summary
    if has_differences(diff_info):
        print(f"\n\033[1;31m=== Comparison Complete: Differences Found Between Directories ===\033[0m")
        sys.exit(1)  # exit code 1 when differences found
    else:
        print(f"\n\033[1;32m=== Comparison Complete: Directories Are Identical ===\033[0m")
        sys.exit(0)  # exit code 0 when no differences


if __name__ == "__main__":
    main()