CODE = """\
        import zipfile
        file = zipfile.ZipFile("library.zip", "r")
        names = []
        for name in file.namelist():
            if name.startswith("timelinelib/plugin/plugins"):
                name = name.rsplit("/", 1)[1]
                if name.endswith(".pyc") and not name.startswith("__"):
                    print name.split(".")[0]
                    names.append(name.split(".")[0])
        f = open("test.txt", "w")
        f.write(" ".join(names))
        f.close()
        return [self._import_module("timelinelib.plugin.plugins.%s" % mod) for mod in names]
"""


FILE = "timelinelib\\plugin\\factory.py"
f = open(FILE, "r")
text = f.read()
f.close()
f = open(FILE, "w")
lines = text.split("\n")
state = 0
for line in lines:
    print line
    if state == 1:
        if len(line.strip()) == 0:
            f.write(line + "\n")
            state = 0
    else:
        if "def _get_candidate_modules(self):" in line:
            print "def"
            f.write(line + "\n")
            f.write(CODE)
            state = 1
        else:
            f.write(line + "\n")
f.write("\n")        
f.write("import timelinelib.plugin.plugins.gradienteventboxdrawer\n")
f.close()
