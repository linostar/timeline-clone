VERSION = (0, 2, 0)
DEV = True


def get_version():
    if DEV:
        return "%s.%s.%sdev" % VERSION
    return "%s.%s.%s" % VERSION
