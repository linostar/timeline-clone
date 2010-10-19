; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=Timeline
AppVerName=Timeline 0.11.0
AppPublisher=Rickard Lindberg <ricli85@gmail.com>
AppPublisherURL=http://thetimelineproj.sourceforge.net/
AppSupportURL=http://thetimelineproj.sourceforge.net/
AppUpdatesURL=http://thetimelineproj.sourceforge.net/
DefaultDirName={pf}\Timeline
DefaultGroupName=Timeline
SourceDir=W:\Projects\Hg\win\timeline
LicenseFile=COPYING
InfoBeforeFile=..\inno\WINSTALL
OutputDir=..\bin
OutputBaseFilename=SetupTimeline0110Std
Compression=lzma
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"


[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "help_resources\*"; DestDir: "{app}\help_resources";  Flags: ignoreversion
Source: "timeline.py"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "timelinelib\*.py"; DestDir: "{app}\timelinelib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icalendar\*.py"; DestDir: "{app}\icalendar"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "po\ca\LC_MESSAGES\*"; DestDir: "{app}\po\ca\LC_MESSAGES"; Flags: ignoreversion
Source: "po\de\LC_MESSAGES\*"; DestDir: "{app}\po\de\LC_MESSAGES"; Flags: ignoreversion
Source: "po\es\LC_MESSAGES\*"; DestDir: "{app}\po\es\LC_MESSAGES"; Flags: ignoreversion
Source: "po\fr\LC_MESSAGES\*"; DestDir: "{app}\po\fr\LC_MESSAGES"; Flags: ignoreversion
Source: "po\he\LC_MESSAGES\*"; DestDir: "{app}\po\he\LC_MESSAGES"; Flags: ignoreversion
Source: "po\it\LC_MESSAGES\*"; DestDir: "{app}\po\it\LC_MESSAGES"; Flags: ignoreversion
Source: "po\pl\LC_MESSAGES\*"; DestDir: "{app}\po\pl\LC_MESSAGES"; Flags: ignoreversion
Source: "po\pt\LC_MESSAGES\*"; DestDir: "{app}\po\pt\LC_MESSAGES"; Flags: ignoreversion
Source: "po\pt_BR\LC_MESSAGES\*"; DestDir: "{app}\po\pt_BR\LC_MESSAGES"; Flags: ignoreversion
Source: "po\ru\LC_MESSAGES\*"; DestDir: "{app}\po\ru\LC_MESSAGES"; Flags: ignoreversion
Source: "po\sv\LC_MESSAGES\*"; DestDir: "{app}\po\sv\LC_MESSAGES"; Flags: ignoreversion
Source: "po\tr\LC_MESSAGES\*"; DestDir: "{app}\po\tr\LC_MESSAGES"; Flags: ignoreversion

;Source: "..\inno\run.pyw"; DestDir: "{app}"; Flags: ignoreversion;
Source: "..\inno\Timeline.ico"; DestDir: "{app}\icons"; Flags: ignoreversion
Source: "..\inno\setup.py"; DestDir: "{app}"; Flags: ignoreversion

Source: "C:\Program Files\Python25\lib\site-packages\wx-2.8-msw-unicode\wx\MSVCP71.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Program Files\Python25\lib\site-packages\wx-2.8-msw-unicode\wx\gdiplus.dll"; DestDir: "{app}"; Flags: ignoreversion


[UninstallDelete]
Type: files; Name: "{app}\*.pyc"
Type: files; Name: "{app}\timelinelib\*.pyc"
Type: files; Name: "{app}\timelinelib\db\*.pyc"
Type: files; Name: "{app}\timelinelib\db\backends\*.pyc"
Type: files; Name: "{app}\timelinelib\drawing\*.pyc"
Type: files; Name: "{app}\timelinelib\drawing\drawers\*.pyc"
Type: files; Name: "{app}\timelinelib\gui\*.pyc"
Type: files; Name: "{app}\timelinelib\gui\components\*.pyc"
Type: files; Name: "{app}\timelinelib\gui\dialogs\*.pyc"
Type: files; Name: "{app}\icalendar\*.pyc"

[Icons]
Name: "{commondesktop}\Timeline"; Filename:"{app}\run.pyw"; IconFilename: "{app}\icons\Timeline.ico";Tasks: desktopicon

[CustomMessages]

[Run]
;Filename: "{app}\run.pyw"; Description: "{cm:LaunchProgram,Timeline}"; Flags: shellexec postinstall skipifsilent unchecked;
Filename: "C:\Program Files\Python25\python.exe"; WorkingDir: "{app}"; Parameters: "setup.py py2exe"; Description: "Start Py2Exe"; Flags: postinstall nowait skipifsilent

[Code]
var
  PythonPath : String;
  InstallPath : String;

function InitializeSetup(): Boolean;
var
  Names      : TArrayOfString;
  i          : Integer;
  PythonFound: Boolean;
  WxPythonFound: Boolean;
  Key        : String;
  Path       : String;
  wxs        : TArrayOfString;
begin
    Key := 'Software\Python\PythonCore\2.5';
    //
    // Try to find python registered under Current User
    //
    PythonFound :=  RegGetSubkeyNames(HKEY_CURRENT_USER, Key , Names);
    if PythonFound then
    begin
        Key := Key + '\InstallPath';
        if not RegQueryStringValue(HKEY_CURRENT_USER, Key, '', InstallPath) then
        begin
          PythonFound := False;
        end;
    end
    //
    // Try to find python registered under Local Machine
    //
    else begin
      PythonFound := RegGetSubkeyNames(HKEY_LOCAL_MACHINE, Key, Names);
      if PythonFound then
      begin
        Key := Key + '\InstallPath';
        if not RegQueryStringValue(HKEY_LOCAL_MACHINE, Key, '', InstallPath) then
        begin
          PythonFound := False;
        end;
      end
    end;

    //
    // Python found... Continue installation
    //
    if PythonFound then
    begin
      Result := True
    end;

    //
    // If Python installation not found... Continue anyway ?
    //
    if not PythonFound then
    begin
      Result := False;
      if MsgBox('Cant find python:' #13#13 'Python version 2.5 must be installed first.' #13 'Continue Setup anyway?', mbInformation, MB_YESNO)= IDYES then
      begin
        Result := True
      end
    end

    //
    // Try find wxPython if installation is to be continued
    //
    if Result then
    begin
       WxPythonFound := False;
       //MsgBox(InstallPath, mbInformation, MB_OK);
       InstallPath := InstallPath + 'Lib\site-packages'
       //
       // Hmm not so nice!
       //
       SetArrayLength(wxs, 2)
       wxs[0] := '\wx-2.8-msw-ansi' ;
       wxs[1] := '\wx-2.8-msw-unicode' ;
       for i := 0 to GetArrayLength(wxs)-1 do begin
         path := InstallPath + wxs[i]
         //MsgBox(path, mbInformation, MB_OK);
         if DirExists(path) then
         begin
           WxPythonFound := True;
         end
       end

       //
       // wxPython found... Continue installation
       //
       if WxPythonFound then
       begin
         Result := True
       end;

    //
    // If wxPython installation not found... Continue anyway ?
    //
       if not WxPythonFound then
       begin
         Result := False
         if MsgBox('Cant find wxPython:' #13#13 'wxPython version 2.8 must be installed first.' #13 'Continue Setup anyway?', mbInformation, MB_YESNO) = IDYES then
         begin
           Result := True
         end
       end
    end

end;
