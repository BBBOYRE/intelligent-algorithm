import subprocess
import os
import sys
import shutil

def run_command(command, cwd=None):
    print(f"Running: {command}")
    process = subprocess.Popen(command, shell=True, cwd=cwd)
    process.wait()
    if process.returncode != 0:
        print(f"Error executing: {command}")
        sys.exit(1)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(root_dir, "frontend")
    scripts_dir = os.path.dirname(os.path.abspath(__file__))

    print("=== Step 1: Building Vue Frontend ===")
    run_command("yarn build", cwd=frontend_dir)

    print("\n=== Step 2: Building PyInstaller Executable ===")
    run_command("pyinstaller scripts/app.spec --clean -y --workpath build/build --distpath build/dist", cwd=root_dir)

    print("\n=== Step 2.5: Copying External Assets ===")
    dist_app_dir = os.path.join(root_dir, "build", "dist", "IntelligentDocSystem")
    try:
        shutil.copy(os.path.join(root_dir, ".env.example"), os.path.join(dist_app_dir, ".env"))
        print(f"Copied .env to {dist_app_dir}")
        models_src = os.path.join(root_dir, "data", "models")
        models_dst = os.path.join(dist_app_dir, "data", "models")
        if os.path.exists(models_src):
            shutil.copytree(models_src, models_dst, dirs_exist_ok=True)
            print(f"Copied {models_src} to {models_dst}")
    except Exception as e:
        print(f"Failed to copy assets: {e}")

    print("\n=== Step 3: Compiling Inno Setup Installer ===")
    print("If you have Inno Setup installed, you can now run:")
    print('iscc scripts/installer.iss')
    print("\nDone! Built executable is in build/dist/IntelligentDocSystem/")

if __name__ == '__main__':
    main()
