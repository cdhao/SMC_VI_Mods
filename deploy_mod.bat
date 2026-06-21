```bat
@echo off
setlocal

rem 当前脚本所在目录
set "PROJECT_DIR=%~dp0"

rem MOD 源目录
set "SOURCE_DIR=%PROJECT_DIR%mods\GraceAshcroft"

rem 文明6 MOD 目标目录
set "TARGET_DIR=C:\Users\82443\Documents\My Games\Sid Meier's Civilization VI\Mods\GraceAshcroft"

echo ========================================
echo Deploying GraceAshcroft MOD
echo ========================================

rem 检查源目录
if not exist "%SOURCE_DIR%\" (
    echo [ERROR] Source directory does not exist:
    echo %SOURCE_DIR%
    pause
    exit /b 1
)

rem 删除旧版本
if exist "%TARGET_DIR%\" (
    echo [1/2] Removing old MOD...
    rmdir /s /q "%TARGET_DIR%"

    if exist "%TARGET_DIR%\" (
        echo [ERROR] Failed to remove old MOD:
        echo %TARGET_DIR%
        pause
        exit /b 1
    )
) else (
    echo [1/2] Old MOD directory does not exist. Skipping removal.
)

rem 复制新版本
echo [2/2] Copying new MOD...

robocopy "%SOURCE_DIR%" "%TARGET_DIR%" /E /COPY:DAT /DCOPY:DAT /R:2 /W:1

rem Robocopy 返回码 0-7 均表示成功
if errorlevel 8 (
    echo.
    echo [ERROR] MOD deployment failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo GraceAshcroft deployed successfully.
echo Target: %TARGET_DIR%
echo ========================================

pause
exit /b 0
```
