FILE = "timeline.py"
f = open(FILE, "r")
text = f.read()
f.close()
f = open(FILE, "w")
lines = text.split("\n")
for line in lines:
    if line[0:16] == "sys.path.insert(":
        f.write("exepath = os.path.dirname(unicode(sys.executable, sys.getfilesystemencoding()))\n")
        f.write("sys.path.insert(0, exepath)\n")
    else:
        f.write(line + "\n")
f.close()


