#define MyAppName "KiCad RPC"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "The Collector"
#define MyAppExeName "KiCad-RPC.exe"

[Setup]

AppId={{0ba08cdc-f8c2-40f8-8097-d9aa52fc9ddc}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\KiCad RPC
DefaultGroupName={#MyAppName}

OutputDir=..\installer-output
OutputBaseFilename=KiCad-RPC-Setup

SetupIconFile=..\assets\kicad-rpc-icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

Compression=lzma
SolidCompression=yes
WizardStyle=modern

PrivilegesRequired=admin


[Files]

Source: "..\executable\dist\KiCad-RPC.exe"; DestDir: "{app}"; Flags: ignoreversion


[Icons]

Name: "{group}\KiCad RPC"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall KiCad RPC"; Filename: "{uninstallexe}"
Name: "{userstartup}\KiCad RPC"; Filename: "{app}\{#MyAppExeName}"


[Run]

Filename: "{app}\{#MyAppExeName}"; Description: "Launch KiCad RPC"; Flags: nowait postinstall skipifsilent
