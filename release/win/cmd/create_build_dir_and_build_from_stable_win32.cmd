set BUILD_DIR=c:\temp\timeline

del /S /Q %BUILD_DIR%\stable
rmdir /S /Q %BUILD_DIR%\stable
rmdir /S /Q %BUILD_DIR%\stable

xcopy /S c:\projekt\timeline\stable %BUILD_DIR%\stable\

cd %BUILD_DIR%\stable\release\win\cmd

build_install_win32_exe.cmd