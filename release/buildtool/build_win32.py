import subprocess


def main():
    p = subprocess.Popen(["python", "build.py", "win32"])
    p.communicate()
    
    
if __name__ == "__main__":
    main()
