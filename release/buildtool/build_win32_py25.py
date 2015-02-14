import subprocess


def main():
    p = subprocess.Popen(["python", "build.py", "win32py25"])
    p.communicate()
    
    
if __name__ == "__main__":
    main()
