
FILE = "inno\\timelineWin32_2.iss"
VERSIONFILE = "timelinelib\\meta\\version.py"

def get_version():
    f = open(VERSIONFILE, "r")
    text = f.read()
    lines = text.split("\n")
    for line in lines:
        if line[0:7] == "VERSION":
            break
    f.close()
    #VERSION = (0, 14, 0)
    line = line.split("(", 1)[1]
    line = line.split(")", 1)[0]
    major, minor, bug = line. split(", ")
    app_ver_name = "Timeline %s.%s.%s" % (major, minor, bug)
    output_base_filename = "SetupTimeline%s%s%sPy2ExeWin32" % (major, minor, bug)
    return (app_ver_name, output_base_filename)

def modify_iss_file(app_ver_name, output_base_filename):
    f = open(FILE, "r")
    text = f.read()
    f.close()
    f = open(FILE, "w")
    lines = text.split("\n")
    for line in lines:
        if line[0:11] == "AppVerName=":
            f.write("AppVerName=%s\n" % app_ver_name)
        elif line[0:19] == "OutputBaseFilename=":
            f.write("OutputBaseFilename=%s\n" % output_base_filename)
        else:
            f.write(line + "\n")

app_ver_name, output_base_filename = get_version()
modify_iss_file(app_ver_name, output_base_filename)

