@echo off
rem This script builds the Timeline installation executable
rem for the Windows target os.

set TIMELINE_DIR=..\..\..\
set PACKAGE_DIR=..

echo ***. Copying icalendar package to timeline directory.
mkdir %TIMELINE_DIR%\icalendar
copy %PACKAGE_DIR%\icalendar\*.*  %TIMELINE_DIR%\icalendar\*.*

echo ***. Copying pysvg package to timeline directory.
mkdir %TIMELINE_DIR%\pysvg
copy %PACKAGE_DIR%\pysvg\*.*  %TIMELINE_DIR%\pysvg\*.*

echo *** Copying setup.py to timeline directory
copy ..\inno\setup.py  %TIMELINE_DIR%\setup.py

echo *** Copying timeline.ico to icons directory
copy ..\inno\Timeline.ico  %TIMELINE_DIR%\icons\Timeline.ico

echo ***. Modifyng timeline.py
python mod_timeline_py.py  > %TIMELINE_DIR%\timeline_tmp.py
del %TIMELINE_DIR%\timeline.py
ren %TIMELINE_DIR%\timeline_tmp.py timeline.py

echo ***. Modifyng paths.py
python mod_paths_py.py  > %TIMELINE_DIR%\timelinelib\paths_tmp.py
del %TIMELINE_DIR%\timelinelib\paths.py
ren %TIMELINE_DIR%\timelinelib\paths_tmp.py paths.py

echo ***. Modifyng timeline.iss
python mod_timeline_iss.py  > ..\inno\timeline_tmp.iss
del ..\inno\timeline.iss
ren ..\inno\timeline_tmp.iss timeline.iss

echo *** Running scons command
pushd %TIMELINE_DIR%
call scons
popd

echo *** Running py2exe
pushd %TIMELINE_DIR%
setup.py py2exe
popd

echo ***. Copying help_resources to dist directory.
mkdir %TIMELINE_DIR%\dist\help_resources
copy %TIMELINE_DIR%\help_resources\*.*  %TIMELINE_DIR%\dist\help_resources\*.*

echo ***. Copying icons to dist directory.
mkdir %TIMELINE_DIR%\dist\icons
copy %TIMELINE_DIR%\icons\*.*  %TIMELINE_DIR%\dist\icons\*.*

echo ***. Copying po to dist directory.
mkdir %TIMELINE_DIR%\dist\po
xcopy %TIMELINE_DIR%\po\*.*  %TIMELINE_DIR%\dist\po\*.* /S
del %TIMELINE_DIR%\dist\po\*.po
del %TIMELINE_DIR%\dist\po\*.pot

echo ***. Compile Inno Std script
pushd  ..\inno
set PATH=%PATH%;"C:\Program Files\Inno Setup 5"
call iscc.exe Timeline.iss

