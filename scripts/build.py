import subprocess
import os
import sys
import shutil

def run_command(command, cwd=None):
    printable = command if isinstance(command, str) else " ".join(command)
    print(f"Running: {printable}")

    try:
        result = subprocess.run(command, cwd=cwd)
    except FileNotFoundError:
        # On Windows, npm/yarn/corepack are often .cmd files and may fail direct spawn.
        if isinstance(command, list):
            fallback_command = subprocess.list2cmdline(command)
        else:
            fallback_command = command
        print(f"Direct execution failed, retrying with shell: {fallback_command}")
        result = subprocess.run(fallback_command, cwd=cwd, shell=True)

    if result.returncode != 0:
        print(f"Error executing: {printable}")
        sys.exit(1)


def detect_frontend_build_command(frontend_dir):
    yarn_lock = os.path.join(frontend_dir, "yarn.lock")
    package_lock = os.path.join(frontend_dir, "package-lock.json")

    npm_available = shutil.which("npm") is not None
    yarn_available = shutil.which("yarn") is not None
    corepack_available = shutil.which("corepack") is not None

    # Prefer npm when package-lock exists to match lockfile and avoid Yarn missing issues.
    if os.path.exists(package_lock) and npm_available:
        return ["npm", "run", "build"]

    if os.path.exists(yarn_lock):
        if yarn_available:
            return ["yarn", "build"]
        if corepack_available:
            return ["corepack", "yarn", "build"]

    if npm_available:
        return ["npm", "run", "build"]

    raise RuntimeError("No available package manager found. Please install npm or yarn.")


def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=== Step 1: Building Vue Frontend ===")
    try:
        frontend_build_cmd = detect_frontend_build_command(frontend_dir)
    except RuntimeError as e:
        print(str(e))
        sys.exit(1)
    run_command(frontend_build_cmd, cwd=frontend_dir)

    print("\n=== Step 2: Building PyInstaller Executable ===")
    pyi_work_dir = os.path.join(root_dir, "build", "build")
    pyi_dist_dir = os.path.join(root_dir, "build", "dist")
    os.makedirs(pyi_work_dir, exist_ok=True)
    os.makedirs(pyi_dist_dir, exist_ok=True)
    os.makedirs(os.path.join(pyi_work_dir, "app"), exist_ok=True)

    run_command(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "scripts/app.spec",
            "--clean",
            "-y",
            "--workpath",
            "build/build",
            "--distpath",
            "build/dist",
        ],
        cwd=root_dir,
    )

    print("\n=== Step 2.5: Copying External Assets ===")
    dist_app_dir = os.path.join(root_dir, "build", "dist", "IntelligentDocSystem")
    try:
        env_src = os.path.join(root_dir, ".env")
        if not os.path.exists(env_src):
            env_src = os.path.join(root_dir, ".env.example")
        shutil.copy(env_src, os.path.join(dist_app_dir, ".env"))
        print(f"Copied {os.path.basename(env_src)} to {dist_app_dir}/.env")
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