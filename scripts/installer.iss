[Setup]
AppName=Intelligent Document System
AppVersion=1.0.0
DefaultDirName={autopf}\IntelligentDocSystem
DefaultGroupName=Intelligent Document System
OutputDir=..\build\Installer
OutputBaseFilename=Install_IntelligentDocSystem
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\app_icon.ico
UninstallDisplayIcon={app}\IntelligentDocSystem.exe
MinVersion=6.1

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\build\dist\IntelligentDocSystem\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Intelligent Document System"; Filename: "{app}\IntelligentDocSystem.exe"
Name: "{group}\Uninstall Intelligent Document System"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Intelligent Document System"; Filename: "{app}\IntelligentDocSystem.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\IntelligentDocSystem.exe"; Description: "{cm:LaunchProgram,Intelligent Document System}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DownloadPage: TDownloadWizardPage;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage(SetupMessage(msgWizardPreparing), SetupMessage(msgPreparingDesc), nil);
end;

function IsWebView2Installed(): Boolean;
var
  version: String;
begin
  Result := False;
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', version) then
  begin
    Result := True;
    Exit;
  end;
  if RegQueryStringValue(HKEY_CURRENT_USER, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', version) then
  begin
    Result := True;
    Exit;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if CurPageID = wpReady then
  begin
    if not IsWebView2Installed() then
    begin
      if MsgBox('运行此程序需要 Microsoft Edge WebView2 运行库。'+#13#10+'你想现在自动下载并安装它吗？', mbConfirmation, MB_YESNO) = IDYES then
      begin
        DownloadPage.Clear;
        DownloadPage.Add('https://go.microsoft.com/fwlink/p/?LinkId=2124703', 'MicrosoftEdgeWebview2Setup.exe', '');
        DownloadPage.Show;
        try
          try
            DownloadPage.Download;
            Exec(ExpandConstant('{tmp}\MicrosoftEdgeWebview2Setup.exe'), '/silent /install', '', SW_SHOW, ewWaitUntilTerminated, ResultCode);
          except
            SuppressibleMsgBox(AddPeriod(GetExceptionMessage), mbCriticalError, MB_OK, IDOK);
            Result := False;
          end;
        finally
          DownloadPage.Hide;
        end;
      end;
    end;
  end;
end;