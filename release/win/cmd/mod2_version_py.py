FILE = "timelinelib\\meta\\version.py"
f = open(FILE, "r")
text = f.read()
f.close()
f = open(FILE, "w")
lines = text.split("\n")
for line in lines:
    if line[0:5] == "DEV =":
        f.write("DEV = False\n")
    else:
        f.write(line + "\n")
f.close()

