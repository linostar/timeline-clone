from subprocess import Popen
import re
import shutil
import os.path
import glob
import tempfile

# extract from
archive_path = "/home/rick/download/launchpad-export.tar.gz"
print archive_path

# extract to
tmp_dir = tempfile.mkdtemp()
print tmp_dir

# extract
Popen(["tar", "xvvz", "-C", tmp_dir, "--file", archive_path]).wait()

# copy po-files
for pofile in glob.glob(os.path.join(tmp_dir, "timeline", "*.po")):
    dest_name = re.search(r".*-(.*.po)", pofile).group(1)
    dest = os.path.join("po", dest_name)
    shutil.copy(pofile, dest)
    print dest

# remove tmp dir
shutil.rmtree(tmp_dir)
