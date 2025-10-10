import os
import sys
import hashlib
from colorama import Fore, init
from safetensors.torch import safe_open
import torch

# Initialize colorama for cross-platform colored output
init(autoreset=True)

def get_safetensors_files(root_dir):
    """Return a sorted list of all .safetensors files under root_dir, with relative paths."""
    file_list = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.safetensors'):
                rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                file_list.append(rel_path)
    return sorted(file_list)

def get_file_hash(file_path, block_size=65536):
    """Compute the MD5 hash of a file for quick comparison."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(block_size)
        while buf:
            hasher.update(buf)
            buf = f.read(block_size)
    return hasher.hexdigest()

def get_safetensors_metadata(file_path):
    """Read metadata from a .safetensors file, compatible with different library versions."""
    metadata = {}
    try:
        with safe_open(file_path, framework="pt", device="cpu") as f:
            # Some versions make metadata a method; call it if needed
            raw_meta = f.metadata() if callable(f.metadata) else (f.metadata or {})
            for key in f.keys():
                info = raw_meta.get(key)
                if info:
                    shape = tuple(info.get("shape", []))
                    dtype = info.get("dtype", "")
                else:
                    tensor = f.get_tensor(key)
                    shape = tuple(tensor.shape)
                    dtype = str(tensor.dtype)
                metadata[key] = {"shape": shape, "dtype": dtype}
        return metadata
    except Exception as e:
        print(f"{Fore.RED}Error reading metadata from {file_path}: {e}")
        return None

def compare_safetensors_structure(file1, file2):
    """Yield structural differences between two .safetensors files."""
    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)
    if size1 != size2:
        yield (f"File size differs: {size1} vs {size2} bytes", "warning")

    meta1 = get_safetensors_metadata(file1)
    meta2 = get_safetensors_metadata(file2)

    if not meta1 or not meta2:
        yield ("Could not read metadata for comparison", "error")
        return

    keys1 = set(meta1.keys())
    keys2 = set(meta2.keys())

    for key in sorted(keys1 - keys2):
        yield (f"Key '{key}' only in first file", "diff")
    for key in sorted(keys2 - keys1):
        yield (f"Key '{key}' only in second file", "diff")

    for key in sorted(keys1 & keys2):
        info1, info2 = meta1[key], meta2[key]
        if info1["shape"] != info2["shape"]:
            yield (f"Key '{key}' shape differs: {info1['shape']} vs {info2['shape']}", "diff")
        if info1["dtype"] != info2["dtype"]:
            yield (f"Key '{key}' dtype differs: {info1['dtype']} vs {info2['dtype']}", "diff")

def compare_directories(dir1, dir2):
    """Compare all .safetensors files in two directories."""
    if not os.path.isdir(dir1):
        print(f"{Fore.RED}Error: Directory {dir1} does not exist")
        return
    if not os.path.isdir(dir2):
        print(f"{Fore.RED}Error: Directory {dir2} does not exist")
        return

    files1 = get_safetensors_files(dir1)
    files2 = get_safetensors_files(dir2)
    common = sorted(set(files1) & set(files2))

    for rel_path in common:
        file1 = os.path.join(dir1, rel_path)
        file2 = os.path.join(dir2, rel_path)
        print(f"{Fore.BLUE}Comparing: {rel_path}")
        diffs = list(compare_safetensors_structure(file1, file2))
        if not diffs:
            print(f"{Fore.GREEN}  No structural differences found")
        else:
            for msg, msg_type in diffs:
                color = Fore.YELLOW if msg_type == "warning" else Fore.RED
                print(f"{color}  {msg}")
        print("-" * 80)

    only1 = sorted(set(files1) - set(files2))
    if only1:
        print(f"{Fore.YELLOW}Files only in {dir1}:")
        for p in only1:
            print(f"  {p}")

    only2 = sorted(set(files2) - set(files1))
    if only2:
        print(f"{Fore.YELLOW}Files only in {dir2}:")
        for p in only2:
            print(f"  {p}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"{Fore.RED}Usage: python compare_safetensors.py <directory1> <directory2>")
        sys.exit(1)
    compare_directories(sys.argv[1], sys.argv[2])
