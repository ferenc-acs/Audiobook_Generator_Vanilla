import subprocess
import sys

def install_ffmpeg():
    # Check if FFmpeg is already installed
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("FFmpeg is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        result = subprocess.run(
            ['choco', 'install', 'ffmpeg', '-y'],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("FFmpeg installed successfully:\n", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Installation failed:\n", e.stderr)
        return False

if __name__ == "__main__":
    success = install_ffmpeg()
    sys.exit(0 if success else 1)