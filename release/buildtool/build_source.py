import subprocess


def main():
    p = subprocess.Popen(["python", "build.py", "source"])
    p.communicate()
    
    
if __name__ == "__main__":
    main()
