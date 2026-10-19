; New Movie Library - Windows setup wizard (NSIS 3).
; Build: makensis plugin-src/installer/NewMovieLibrary.nsi   (tools/build_plugin.sh does this)
;
; The setup is small: it installs the VST3 / CLAP plugin from Plugin\Windows and copies the
; samples from the "New Movie Library" folder of the same download (two folders up), so run it
; from the unzipped download.

Target amd64-unicode
!include "MUI2.nsh"
!include "x64.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

!define APP "New Movie Library"
!define VERSION "1.0.0"
!define UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\NewMovieLibrary"

Name "${APP}"
OutFile "..\..\Plugin\Windows\New Movie Library Setup.exe"
InstallDir "$PROGRAMFILES64\${APP}"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
BrandingText "${APP} ${VERSION}"

Var SampleDir
Var SourceLib

!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_ABORTWARNING
!define MUI_WELCOMEPAGE_TITLE "New Movie Library"
!define MUI_WELCOMEPAGE_TEXT "This installs the New Movie Library player plugin (VST3 and CLAP) and its 45 instruments.$\r$\n$\r$\nRun it from the unzipped download, so it can find the $\"New Movie Library$\" sample folder.$\r$\n$\r$\nClose your DAW before you continue."
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_COMPONENTS

!define MUI_PAGE_HEADER_TEXT "Sample folder"
!define MUI_PAGE_HEADER_SUBTEXT "Where should the 1,527 samples (about 470 MB) go?"
!define MUI_DIRECTORYPAGE_TEXT_TOP "The samples are copied to this folder and the plugin is told where they are. You can choose another drive if C: is short of space."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Sample folder"
!define MUI_DIRECTORYPAGE_VARIABLE $SampleDir
!define MUI_PAGE_CUSTOMFUNCTION_PRE SkipSamplePage
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_TITLE "New Movie Library is installed"
!define MUI_FINISHPAGE_TEXT "Open your DAW, rescan plugins and add $\"New Movie Library$\" to an instrument track.$\r$\n$\r$\nVST3: $COMMONFILES64\VST3$\r$\nCLAP: $COMMONFILES64\CLAP"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Function .onInit
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "New Movie Library needs 64-bit Windows."
    Abort
  ${EndIf}
  SetShellVarContext current
  StrCpy $SampleDir "$DOCUMENTS\${APP}"
  ; the sample folder of the download: <download>\New Movie Library (setup is in <download>\Plugin\Windows)
  GetFullPathName $SourceLib "$EXEDIR\..\..\${APP}"
  ${IfNot} ${FileExists} "$SourceLib\Samples\*.*"
    GetFullPathName $SourceLib "$EXEDIR\${APP}"
  ${EndIf}
FunctionEnd

Function SkipSamplePage
  ${IfNot} ${SectionIsSelected} 2
    Abort
  ${EndIf}
FunctionEnd

Section "VST3 plugin (recommended)" SecVST3
  SectionIn RO
  ${DisableX64FSRedirection}
  SetOutPath "$COMMONFILES64\VST3\NewMovieLibrary.vst3\Contents\x86_64-win"
  File "..\..\Plugin\Windows\NewMovieLibrary.vst3\Contents\x86_64-win\NewMovieLibrary.vst3"
  SetOutPath "$INSTDIR"
  File "..\..\Plugin\README.md"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  SetRegView 64
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayName" "${APP}"
  WriteRegStr HKLM "${UNINST_KEY}" "DisplayVersion" "${VERSION}"
  WriteRegStr HKLM "${UNINST_KEY}" "Publisher" "${APP}"
  WriteRegStr HKLM "${UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${UNINST_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "${UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINST_KEY}" "NoRepair" 1
SectionEnd

Section "CLAP plugin (Bitwig, Reaper, FL Studio 2024+, Studio One 7)" SecCLAP
  ${DisableX64FSRedirection}
  SetOutPath "$COMMONFILES64\CLAP"
  File "..\..\Plugin\Windows\NewMovieLibrary.clap"
SectionEnd

Section "Copy the samples (choose the folder next)" SecSamples
  ${IfNot} ${FileExists} "$SourceLib\Samples\*.*"
    MessageBox MB_ICONEXCLAMATION "The $\"${APP}$\" sample folder was not found next to this setup.$\r$\n$\r$\nThe plugin is installed; when it opens, use $\"Find the sample library$\" to point it to the folder."
    Return
  ${EndIf}
  ${If} $SourceLib == $SampleDir
    DetailPrint "Samples are already in place: $SampleDir"
  ${Else}
    DetailPrint "Copying samples to $SampleDir (this can take a minute)..."
    CreateDirectory "$SampleDir"
    CopyFiles "$SourceLib\*.*" "$SampleDir" 480000
  ${EndIf}
  SetRegView 64
  WriteRegStr HKLM "${UNINST_KEY}" "SampleFolder" "$SampleDir"
SectionEnd

Section "-remember the sample location"
  SetShellVarContext current
  ${If} ${SectionIsSelected} ${SecSamples}
  ${AndIf} ${FileExists} "$SampleDir\Samples\*.*"
    StrCpy $0 $SampleDir
  ${ElseIf} ${FileExists} "$SourceLib\Samples\*.*"
    StrCpy $0 $SourceLib
  ${Else}
    Return
  ${EndIf}
  CreateDirectory "$APPDATA\NewMovieLibrary"
  FileOpen $1 "$APPDATA\NewMovieLibrary\library_path.txt" w
  FileWriteWord $1 0xFEFF
  FileWriteUTF16LE $1 $0
  FileClose $1
  DetailPrint "Sample location saved: $0"
SectionEnd

LangString DESC_VST3 ${LANG_ENGLISH} "The plugin for almost every Windows DAW (Ableton Live, FL Studio, Cubase, Reaper, Studio One, Bitwig...)."
LangString DESC_CLAP ${LANG_ENGLISH} "The same plugin in the newer CLAP format, for DAWs that support it."
LangString DESC_SAMPLES ${LANG_ENGLISH} "Copy the 45 instruments' samples (about 470 MB) to a folder of your choice. Untick to use them from the download folder (keep it in place)."
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecVST3} $(DESC_VST3)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCLAP} $(DESC_CLAP)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecSamples} $(DESC_SAMPLES)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section "Uninstall"
  SetShellVarContext current
  ${DisableX64FSRedirection}
  SetRegView 64
  RMDir /r "$COMMONFILES64\VST3\NewMovieLibrary.vst3"
  Delete "$COMMONFILES64\CLAP\NewMovieLibrary.clap"
  ReadRegStr $0 HKLM "${UNINST_KEY}" "SampleFolder"
  ${If} $0 != ""
  ${AndIf} ${FileExists} "$0\Samples\*.*"
    MessageBox MB_YESNO|MB_DEFBUTTON2 "Also delete the samples in$\r$\n$0 ?" /SD IDNO IDNO keep
    RMDir /r "$0"
    keep:
  ${EndIf}
  RMDir /r "$APPDATA\NewMovieLibrary"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "${UNINST_KEY}"
SectionEnd
