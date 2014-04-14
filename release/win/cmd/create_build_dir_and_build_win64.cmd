set BUILD_DIR=c:\temp\timeline

del /S /Q %BUILD_DIR%\main
rmdir /S /Q %BUILD_DIR%\main
rmdir /S /Q %BUILD_DIR%\main

xcopy /S c:\projekt\timeline\main %BUILD_DIR%\main\

cd %BUILD_DIR%\main\release\win\cmd

build_install_win64_exe.cmd