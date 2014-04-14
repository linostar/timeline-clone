@echo off
rem This script builds the Timeline installation executable
rem for the Windows target os.

set TIMELINE_DIR=..\..\..\
set PACKAGE_DIR=..
set ICALENDAR_DIR=%TIMELINE_DIR%\libs\dependencies\icalendar-3.2\icalendar
set PYTZ_DIR=%TIMELINE_DIR%\libs\dependencies\pytz-2012j\pytz
set PYSVG_DIR=%TIMELINE_DIR%\libs\dependencies\pysvg-0.2.1\pysvg
set MARKDOWN_DIR=%TIMELINE_DIR%\libs\dependencies\markdown-2.0.3\markdown


echo ***. Copying icalendar package to timeline directory.
mkdir %TIMELINE_DIR%\icalendar
copy %ICALENDAR_DIR%\*.*  %TIMELINE_DIR%\icalendar\*.*
rem pause

echo ***. Copying pytz package to timeline directory.
mkdir %TIMELINE_DIR%\pytz
copy %PYTZ_DIR%\*.*  %TIMELINE_DIR%\pytz\*.*
rem pause

echo ***. Copying pysvg package to timeline directory.
mkdir %TIMELINE_DIR%\pysvg
copy %PYSVG_DIR%\*.*  %TIMELINE_DIR%\pysvg\*.*
rem pause

echo ***. Copying markdown package to timeline directory.
mkdir %TIMELINE_DIR%\markdown
copy %MARKDOWN_DIR%\*.*  %TIMELINE_DIR%\markdown\*.*
rem pause

echo *** Copying setup.py to timeline directory
copy ..\inno\setup.py  %TIMELINE_DIR%\setup.py
rem pause

echo *** Copying timeline.ico to icons directory
copy ..\inno\Timeline.ico  %TIMELINE_DIR%\icons\Timeline.ico
rem pause

echo ***. Modifyng timeline.py
python mod_timeline_py.py  > %TIMELINE_DIR%\timeline_tmp.py
del %TIMELINE_DIR%\timeline.py
ren %TIMELINE_DIR%\timeline_tmp.py timeline.py
rem pause

echo ***. Modifyng paths.py
python mod_paths_py.py  > %TIMELINE_DIR%\timelinelib\config\paths_tmp.py
del %TIMELINE_DIR%\timelinelib\config\paths.py
ren %TIMELINE_DIR%\timelinelib\config\paths_tmp.py paths.py
rem pause

echo ***. Modifyng timeline.iss
python mod_timeline_iss_win32.py  > ..\inno\timelineWin32_tmp.iss
rem ren ..\inno\timelineWin32.iss  _timelineWin32.iss
rem ren ..\inno\timelineWin32_tmp.iss timelineWin32.iss
rem pause

echo *** Running scons command
pushd %TIMELINE_DIR%
call scons
popd
rem pause

echo *** Running py2exe
pushd %TIMELINE_DIR%
python setup.py py2exe
popd
rem pause

echo ***. Copying icons to dist directory.
mkdir %TIMELINE_DIR%\dist\icons
copy %TIMELINE_DIR%\icons\*.*  %TIMELINE_DIR%\dist\icons\*.*
rem pause

echo ***. Copying po to dist directory.
mkdir %TIMELINE_DIR%\dist\po
xcopy %TIMELINE_DIR%\po\*.*  %TIMELINE_DIR%\dist\po\*.* /S
del %TIMELINE_DIR%\dist\po\*.po
del %TIMELINE_DIR%\dist\po\*.pot
rem pause

echo ***. Compile Inno Std script
pushd  ..\inno
call "%ProgramFiles%\Inno Setup 5\iscc.exe" timelineWin32_tmp.iss
pause

