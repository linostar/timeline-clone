# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


"""
Working directory = BUILD_DIR
COPYDIR     Copies from TIMELINE_DIR to BUILD_DIR
"""

import sys
import os
import shutil
import subprocess


TIMELINE_DIR = os.path.abspath("..\\")
BUILD_DIR = os.path.abspath(".\\target")

COPYFILE = 0
COPYDIR = 1
MAKEDIR = 2
PUSHD = 3
POPD = 4
RUNCMD = 5
RUNPYSCRIPT = 6
CPYDIR = 7


known_targets = ("win32", "win32py25", "source")


win32_actions = (
                 # Modify some python files
                 (COPYDIR, r"release\win\cmd", "cmd"),
                 (COPYFILE, "timeline.py", "timeline.py"),
                 (RUNPYSCRIPT, r"cmd\mod2_timeline_py.py", ""),
                 (COPYDIR, "timelinelib", "timelinelib"),
                 (RUNPYSCRIPT, r"cmd\mod2_paths_py.py", ""),
                 (RUNPYSCRIPT, r"cmd\mod2_version_py.py", ""),
                 (MAKEDIR, None, "inno"),
                 (COPYFILE, r"release\win\inno\timelineWin32_2.iss", r"inno\timelineWin32_2.iss"),
                 (RUNPYSCRIPT, r"cmd\mod2_timeline_iss_win32.py", ""),
                 # Library dependencies
                 (COPYDIR, r"libs\dependencies\icalendar-3.2\icalendar", "icalendar"),
                 (COPYDIR, r"libs\dependencies\pytz-2012j\pytz", "pytz"),
                 (COPYDIR, r"libs\dependencies\pysvg-0.2.1\pysvg", "pysvg"),
                 (COPYDIR, r"libs\dependencies\markdown-2.0.3\markdown", "markdown"),
                 # Create distribution directory
                 (COPYFILE, r"release\win\inno\setup.py", "setup.py"),
                 (MAKEDIR, None, "icons"),
                 (COPYFILE, r"release\win\inno\Timeline.ico", r"icons\Timeline.ico"),
                 (RUNPYSCRIPT, "setup.py", "py2exe"),
                 # Create distribution executable
                 (COPYFILE, "SConstruct", "SConstruct"),
                 (COPYDIR, "po", "po"),
                 (RUNCMD, "scons.bat", ""),
                 (CPYDIR, "po", r"dist\po"),
                 (COPYDIR, "icons", r"dist\icons"),
                 (COPYFILE, r"release\win\inno\Timeline.ico", r"dist\icons\Timeline.ico"),
                 (COPYFILE, "COPYING", "COPYING"),
                 (COPYFILE, r"release\win\inno\WINSTALL", r"WINSTALL"),
                 (RUNCMD, "iscc.exe", r"inno\timelineWin32_2.iss"),
                 )

win32py25_actions = (
                 # Modify some python files
                 (COPYDIR, r"release\win\cmd", "cmd"),
                 (COPYFILE, "timeline.py", "timeline.py"),
                 (RUNPYSCRIPT, r"cmd\mod2_timeline_py.py", ""),
                 (COPYDIR, "timelinelib", "timelinelib"),
                 (RUNPYSCRIPT, r"cmd\mod2_paths_py.py", ""),
                 (RUNPYSCRIPT, r"cmd\mod2_version_py.py", ""),
                 (MAKEDIR, None, "inno"),
                 (COPYFILE, r"release\win\inno\timelineWin32_py25.iss", r"inno\timelineWin32_2.iss"),
                 (RUNPYSCRIPT, r"cmd\mod2_timeline_iss_win32.py", ""),
                 # Library dependencies
                 (COPYDIR, r"libs\dependencies\icalendar-3.2\icalendar", "icalendar"),
                 (COPYDIR, r"libs\dependencies\pytz-2012j\pytz", "pytz"),
                 (COPYDIR, r"libs\dependencies\pysvg-0.2.1\pysvg", "pysvg"),
                 (COPYDIR, r"libs\dependencies\markdown-2.0.3\markdown", "markdown"),
                 # Create distribution directory
                 (COPYFILE, r"release\win\inno\setup.py", "setup.py"),
                 (MAKEDIR, None, "icons"),
                 (COPYFILE, r"release\win\inno\Timeline.ico", r"icons\Timeline.ico"),
                 (RUNPYSCRIPT, "setup.py", "py2exe"),
                 # Create distribution executable
                 (COPYFILE, "SConstruct", "SConstruct"),
                 (COPYDIR, "po", "po"),
                 (RUNCMD, "scons.bat", ""),
                 (CPYDIR, "po", r"dist\po"),
                 (COPYDIR, "icons", r"dist\icons"),
                 (COPYFILE, r"release\win\inno\Timeline.ico", r"dist\icons\Timeline.ico"),
                 (COPYFILE, "COPYING", "COPYING"),
                 (COPYFILE, r"release\win\inno\WINSTALL", r"WINSTALL"),
                 (RUNCMD, "iscc.exe", r"inno\timelineWin32_2.iss"),
                 )


source_actions = (
                 # Change working dir to TIMELINE_DIR
                 (PUSHD, os.path.join(TIMELINE_DIR, "release"), None),
                 # Create source release artifact
                 (RUNPYSCRIPT, "make-source-release.py", ""),
                 # Restore working dir 
                 (POPD, None, None),
                 )


actions = {"win32": win32_actions,
           "win32py25" : win32py25_actions,
           "source" : source_actions}


class Target():
    def __init__(self, target):
        print "Building target %s" % target
        self.target = target
        self.actions = actions[target]

    def build(self):
        self.define_root_dirs()
        self.create_target_dir()
        self.execute_actions()  
        #self.delete_target_dir()
        
    def define_root_dirs(self):
        self.timeline_dir = os.path.abspath("..\\")
        self.build_dir = os.path.abspath(".\\target")
        print "Source in %s" % self.timeline_dir
        print "Target in %s" % os.getcwd()
        
    def create_target_dir(self):  
        print "Deleting old target"
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
        print "Creating target dir"
        os.mkdir(self.build_dir)
        os.chdir(self.build_dir)

    def delete_target_dir(self):
        os.chdir("..\\")
        shutil.rmtree(self.build_dir)
    
    def execute_actions(self):
        count = 0
        total = len(self.actions)
        try:
            for action, src, dst in self.actions:
                count +=1
                if action == COPYFILE:
                    print "Action %d(%d): COPYFILE %s -> %s" % (count, total, src, os.path.abspath(dst))
                    shutil.copyfile(os.path.join(self.timeline_dir, src), dst)
                if action == COPYDIR:
                    print "Action %d(%d): COPYDIR %s -> %s" % (count, total, src, os.path.abspath(dst))
                    shutil.copytree(os.path.join(self.timeline_dir, src), os.path.join(dst))
                if action == CPYDIR:
                    print "Action %d(%d): CPYDIR %s -> %s" % (count, total, src, os.path.abspath(dst))
                    shutil.copytree(os.path.join(src), os.path.join(dst))
                if action == MAKEDIR:
                    print "Action %d(%d): MAKEDIR %s" % (count, total, os.path.abspath(dst))
                    os.mkdir(os.path.join(self.build_dir, dst))
                if action == RUNPYSCRIPT:
                    print "Action %d(%d): RUNPYSCRIPT %s %s" % (count, total, src, os.path.abspath(dst))
                    success, msg = self.run_pyscript(src, [dst])
                    if not success:
                        print msg
                        break
                if action == RUNCMD:
                    print "Action %d(%d): RUNCMD %s" % (count, total, src)
                    success, msg = self.run_command([src, dst])
                    if not success:
                        print msg
                        break
                if action == PUSHD:
                    self.cwd = os.getcwd()
                    os.chdir(src)
                    print "Action %d(%d): PUSHD %s ->  %s" % (count, total, os.path.abspath(self.cwd),  os.getcwd())
                if action == POPD:
                    os.chdir(self.cwd)
                    print "Action %d(%d): POP %s" % (count, total, self.cwd)
            print "BUILD DONE"
        except Exception, ex:
            print str(ex)
            print "BUILD FAILED"
            
    def run_pyscript(self, script, args=[]):
        return self.run_command(["python", script] + args)

    def run_command(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = p.communicate()
        if p.returncode == 0:
            return True, out[0]
        else:
            return False, out[1]
    

def main():
    if len(sys.argv) == 1:
        print "A target-name must be given as an argument"
    else:
        target = sys.argv[1]
        if target not in known_targets:
            print "%s is an unknown target" % target
        else:
            Target(target).build()
    
    
if __name__ == "__main__":
    main()
