# build_exe.ps1
# Automate the PyInstaller build process

# 1. Clean previous builds
Remove-Item -Path "build", "dist" -Recurse -ErrorAction SilentlyContinue

# 2. Run PyInstaller
# --onefile: single executable
# --windowed: no console
# --icon: use assets/icon.png if possible (converted to .ico or justpng)
# --add-data: include assets
Write-Host "Starting PyInstaller Build..." -ForegroundColor Green

python -m PyInstaller --noconfirm --onefile --windowed `
    --name "aritive's chat spammer" `
    --icon "assets/icon.ico" `
    --add-data "assets;assets" `
    main.py

Write-Host "Build Complete! Check the 'dist' folder." -ForegroundColor Green
