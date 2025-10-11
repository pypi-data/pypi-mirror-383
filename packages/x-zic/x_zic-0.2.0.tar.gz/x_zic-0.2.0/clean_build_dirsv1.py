import os
import shutil

def remove_egg_info_recursively(root="."):
    """
    Recursively remove all directories ending with `.egg-info` starting from `root`.
    """
    for dirpath, dirnames, _ in os.walk(root):
        # Make a copy of dirnames because we may modify it while iterating
        for dirname in dirnames[:]:
            if dirname.endswith(".egg-info"):
                full_path = os.path.join(dirpath, dirname)
                print(f"Removing {full_path}/ ...")
                shutil.rmtree(full_path)
                # remove from dirnames so os.walk doesn't descend into it
                dirnames.remove(dirname)

def remove_pycache(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for d in dirs:
            if d == "__pycache__":
                cache_path = os.path.join(root, d)
                try:
                    shutil.rmtree(cache_path)
                    print(f"[REMOVED] {cache_path}")
                except Exception as e:
                    print(f"[ERROR]   {cache_path} -> {e}")

def clean_build_dirs():
    """
    Remove build artifact directories if they exist:
    - dist/
    - any *.egg-info directory
    """
    # Always check 'dist'
    if os.path.exists("dist"):
        print("Removing dist/ ...")
        shutil.rmtree("dist")
    else:
        print("dist/ not found, skipping.")
        
    # Always check '.pytest_cache'
    if os.path.exists(".pytest_cache"):
        print("Removing dist/ ...")
        shutil.rmtree(".pytest_cache")
    else:
        print(".pytest_cache/ not found, skipping.")
    
    # Always check 'build'
    if os.path.exists("build"):
        print("Removing build/ ...")
        shutil.rmtree("build")
    else:
        print("build/ not found, skipping.")
        
    # Always check 'build'
    if os.path.exists("build"):
        print("Removing build/ ...")
        shutil.rmtree("build")
    else:
        print("build/ not found, skipping.") 
    
    remove_egg_info_recursively()
    
    folder_to_clean = "."   # current folder, change if needed
    remove_pycache(folder_to_clean)


if __name__ == "__main__":
    clean_build_dirs()