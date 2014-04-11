
def get_version():
    f = open("..\\..\\..\\timelinelib\\meta\\version.py", "r")
    text = f.read()
    lines = text.split("\n")
    for line in lines:
        if line[0:7] == "VERSION":
            version_line = line
            break
    f.close()
    line = line.split("(", 1)[1]
    line = line.split(")", 1)[0]
    major, minor, bug = line. split(", ")
    app_ver_name = "Timeline %s.%s.%s" % (major, minor, bug)
    output_base_filename = "SetupTimeline%s%s%sPy2ExeWin64" % (major, minor, bug)
    return (app_ver_name, output_base_filename)

def modify_iss_file(app_ver_name, output_base_filename):
    f = open("..\\inno\\timelineWin64.iss", "r")
    text = f.read()
    lines = text.split("\n")
    for line in lines:
        if line[0:11] == "AppVerName=":
            print "AppVerName=%s" % app_ver_name
        elif line[0:19] == "OutputBaseFilename=":
            print "OutputBaseFilename=%s" % output_base_filename
        else:
            print line
    f.close()

app_ver_name, output_base_filename = get_version()
modify_iss_file(app_ver_name, output_base_filename)

