; ===========================================================================
;  AIC — Audio Intelligence Companion
;  Inno Setup Script
;
;  Usage (GitHub Actions / local) :
;    iscc /DMyAppVersion="2.1.0" installer\AIC.iss
;
;  La version est passée via /DMyAppVersion pour éviter tout hardcode.
;  Tous les chemins sont relatifs à l'emplacement du .iss (installer\).
;  Aucun chemin absolu lié au poste développeur.
; ===========================================================================

#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

; ---------------------------------------------------------------------------
; Métadonnées de l'application
; ---------------------------------------------------------------------------
#define MyAppName        "AIC"
#define MyAppFullName    "AIC — Audio Intelligence Companion"
#define MyAppPublisher   "Flex1 Tech"
#define MyAppURL         "https://github.com/Flex1-tech/Local_Recommendation_Engine"
#define MyAppSupportURL  "https://github.com/Flex1-tech/Local_Recommendation_Engine/issues"
#define MyAppExeName     "AIC.exe"
#define MyAppCopyright   "Copyright © 2026 Flex1 Tech"

; Chemins relatifs au fichier .iss (installer/)
#define BuildDir    "..\build\windows"
#define IconFile    "..\assets\icon.ico"
#define OutputDir   "Output"

[Setup]
; Identifiant unique — NE PAS modifier entre les versions (requis pour mises à jour)
AppId={{F4A7C2D1-3B8E-4F9A-A6E2-1D5C8B7F0E3A}

AppName={#MyAppFullName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppFullName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppSupportURL}
AppUpdatesURL={#MyAppURL}/releases
AppCopyright={#MyAppCopyright}

; Répertoire d'installation standard Windows (Program Files)
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppFullName}
AllowNoIcons=yes

; Sortie
OutputDir={#SourcePath}\{#OutputDir}
OutputBaseFilename=AIC-Setup-{#MyAppVersion}

; Icône de l'installateur
SetupIconFile={#SourcePath}\{#IconFile}
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppFullName}

; Compression maximale (taille de téléchargement réduite)
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Architecture
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Comportement de l'installateur
MinVersion=10.0
DisableProgramGroupPage=yes
DisableReadyPage=no
ShowLanguageDialog=auto

; Privilèges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Langue
[Languages]
Name: "english";  MessagesFile: "compiler:Default.isl"
Name: "french";   MessagesFile: "compiler:Languages\French.isl"

; ---------------------------------------------------------------------------
; Tâches optionnelles (raccourci bureau)
; ---------------------------------------------------------------------------
[Tasks]
Name: "desktopicon"; \
  Description: "{cm:CreateDesktopIcon}"; \
  GroupDescription: "{cm:AdditionalIcons}"; \
  Flags: unchecked

; ---------------------------------------------------------------------------
; Fichiers
; Source : bundle complet build\windows\ (one-folder Flet)
; Préserve toute l'arborescence, y compris les sous-dossiers cachés
; ---------------------------------------------------------------------------
[Files]
Source: "{#SourcePath}\{#BuildDir}\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs; \
  Excludes: "*.pdb"

; ---------------------------------------------------------------------------
; Raccourcis
; ---------------------------------------------------------------------------
[Icons]
; Menu Démarrer
Name: "{group}\{#MyAppFullName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\{#MyAppExeName}"; \
  Comment: "Lancer AIC — Audio Intelligence Companion"

; Désinstallation dans le Menu Démarrer
Name: "{group}\Désinstaller {#MyAppFullName}"; \
  Filename: "{uninstallexe}"

; Raccourci Bureau (conditionnel à la tâche optionnelle)
Name: "{autodesktop}\{#MyAppFullName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  IconFilename: "{app}\{#MyAppExeName}"; \
  Tasks: desktopicon; \
  Comment: "Lancer AIC — Audio Intelligence Companion"

; ---------------------------------------------------------------------------
; Lancement optionnel après installation
; ---------------------------------------------------------------------------
[Run]
Filename: "{app}\{#MyAppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(MyAppFullName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

; ---------------------------------------------------------------------------
; Nettoyage à la désinstallation (données utilisateur exclues)
; Le répertoire %APPDATA%\AIC n'est PAS supprimé (données utilisateur)
; ---------------------------------------------------------------------------
[UninstallDelete]
Type: filesandordirs; Name: "{app}"
