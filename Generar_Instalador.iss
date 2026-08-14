; Generar_Instalador.iss — Script Oficial Inno Setup para XDS AI Assistant
[Setup]
AppId={{94F69B89-2B3D-4A2D-A2A9-9C5B726F8012}}
AppName=XDS AI Assistant
AppVersion=1.0.0
AppPublisher=Xdata Security
AppPublisherURL=https://www.xdatasecurity.com
AppSupportURL=https://www.xdatasecurity.com
AppUpdatesURL=https://www.xdatasecurity.com
DefaultDirName={localappdata}\XDS_AI
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=.\DIST_INSTALADOR_ASISTENTE_XDS
OutputBaseFilename=Instalar_XDS_Oficial
SetupIconFile=.\assets\jarvis_icono.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\XDS_AI.exe

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: ".\dist\XDS_AI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\XDS AI Assistant"; Filename: "{app}\XDS_AI.exe"; IconFilename: "{app}\XDS_AI.exe"
Name: "{autodesktop}\XDS AI Assistant"; Filename: "{app}\XDS_AI.exe"; IconFilename: "{app}\XDS_AI.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\XDS_AI.exe"; Description: "{cm:LaunchProgram,XDS AI Assistant}"; Flags: nowait postinstall skipifsilent