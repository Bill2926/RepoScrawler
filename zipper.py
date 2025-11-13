import os
import subprocess

# Paths
main_folder = r"C:\Users\Admin\Desktop\github-scaper\cloned_repo_zipped"
seven_zip = r"C:\Program Files\7-Zip\7z.exe"  # Full path to 7z.exe

def compress_all():
    print("Compressing folders...\n")
    for item in os.listdir(main_folder):
        folder_path = os.path.join(main_folder, item)

        if os.path.isdir(folder_path):
            zip_path = os.path.join(main_folder, f"{item}.zip")

            # Skip if zip already exists
            if os.path.exists(zip_path):
                print(f"Skip: {zip_path} already exists.")
                continue

            cmd = [seven_zip, "a", "-tzip", zip_path, folder_path]
            print(f"Compressing: {folder_path} -> {zip_path}")
            subprocess.run(cmd, check=True)

    print("\nDone: all folders processed.")

def unzip_all():
    print("Extracting zip files...\n")
    for item in os.listdir(main_folder):
        if item.lower().endswith(".zip"):
            zip_path = os.path.join(main_folder, item)
            extract_folder = os.path.join(main_folder, os.path.splitext(item)[0])

            # Skip if already extracted
            if os.path.exists(extract_folder):
                print(f"Skip: {extract_folder} already exists.")
                continue

            cmd = [seven_zip, "x", zip_path, f"-o{extract_folder}", "-y"]
            print(f"Extracting: {zip_path} -> {extract_folder}")
            subprocess.run(cmd, check=True)

    print("\nDone: all zip files processed.")

if __name__ == "__main__":
    choice = input("Type 'z' to compress or 'u' to extract: ").strip().lower()

    if choice == "z":
        compress_all()
    elif choice == "u":
        unzip_all()
    else:
        print("Invalid choice. Please type 'z' or 'u'.")