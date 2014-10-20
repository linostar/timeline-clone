FILE = "timelinelib\\config\\paths.py"
f = open(FILE, "r")
text = f.read()
f.close()
f = open(FILE, "w")
lines = text.split("\n")
for line in lines:
    if line[0:7] == "_ROOT =":
        f.write("import sys\n")
        f.write("_ROOT = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))\n")
    else:
        f.write(line + "\n")
f.close()

