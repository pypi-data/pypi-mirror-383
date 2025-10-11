You're on Windows PowerShell, so the `||` syntax doesn't work. Let me give you the correct PowerShell commands and continue with the setup:

## 1. Fix PowerShell Commands for Tag Management

```powershell
# Remove old tags (PowerShell syntax)
git tag -d v0.1.5
if ($LASTEXITCODE -ne 0) { Write-Host "Tag v0.1.5 didn't exist or already deleted" }

# Remove remote tag
git push origin --delete v0.1.5
if ($LASTEXITCODE -ne 0) { Write-Host "Remote tag v0.1.5 didn't exist or already deleted" }

# Push your changes first
git push origin main
```

## 2. Create Proper Annotated Tag

```powershell
# Create annotated tag
git tag -a v0.1.5 -m "Release version 0.1.5 - Dynamic versioning"

# Push the tag to remote
git push origin v0.1.5
```

## 3. Verify Tag Creation

```powershell
# Check the tag was created correctly
git show v0.1.5

# List all tags
git tag -l

# Check current commit matches the tag
git describe --tags --exact-match
```

## 4. Build from Tagged Commit

```powershell
# Make sure you're on the tagged commit
git checkout v0.1.5

# Clean build directories
python clean_build_dirs.py

# Build the package
python -m build
```

## 5. Verify Clean Version

```powershell
# Check what was built
Get-ChildItem dist/

# Install and test
pip install dist/x_zic-0.1.5-py3-none-any.whl

# Check the version - should be clean "0.1.5"
python -c "import x_zic; print(f'Version: {x_zic.__version__}')"

# If you get an error about the package not being installed, try:
pip install --force-reinstall dist/x_zic-0.1.5-py3-none-any.whl
```

## 6. Complete PowerShell Script for Future Releases

Create a file `release.ps1` for future releases:

```powershell
# release.ps1 - PowerShell release script
param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

Write-Host "🚀 Starting release process for version $Version" -ForegroundColor Green

# Step 1: Clean and prepare
Write-Host "`nStep 1: Cleaning build directories..." -ForegroundColor Yellow
python clean_build_dirs.py

# Step 2: Make sure we're on main and up to date
Write-Host "`nStep 2: Updating main branch..." -ForegroundColor Yellow
git checkout main
git pull origin main

# Step 3: Remove old tag if exists
Write-Host "`nStep 3: Removing old tag v$Version..." -ForegroundColor Yellow
git tag -d "v$Version" 2>$null
git push origin --delete "v$Version" 2>$null

# Step 4: Create new annotated tag
Write-Host "`nStep 4: Creating new tag v$Version..." -ForegroundColor Yellow
git tag -a "v$Version" -m "Release version $Version"
git push origin "v$Version"

# Step 5: Build from tagged commit
Write-Host "`nStep 5: Building package from tag v$Version..." -ForegroundColor Yellow
git checkout "v$Version"
python -m build

# Step 6: Verify the build
Write-Host "`nStep 7: Verifying build..." -ForegroundColor Yellow
$wheel = Get-ChildItem dist/*.whl | Select-Object -First 1
if ($wheel) {
    Write-Host "✅ Built: $($wheel.Name)" -ForegroundColor Green
    
    # Test installation
    pip install --force-reinstall $wheel.FullName
    $result = python -c "import x_zic; print(x_zic.__version__)" 2>$null
    if ($result -eq $Version) {
        Write-Host "✅ Version verified: $result" -ForegroundColor Green
    } else {
        Write-Host "❌ Version mismatch: expected $Version, got $result" -ForegroundColor Red
    }
} else {
    Write-Host "❌ No wheel file found in dist/" -ForegroundColor Red
}

# Step 7: Go back to main for development
Write-Host "`nStep 8: Returning to main branch..." -ForegroundColor Yellow
git checkout main

Write-Host "`n🎉 Release process completed!" -ForegroundColor Green
```

## 7. Use the Release Script

```powershell
# Run the release script for version 0.1.5
.\release.ps1 -Version "0.1.5"

# Or for future versions
.\release.ps1 -Version "0.1.6"
```

## 8. If You Encounter Issues During Build

If you still get warnings or the version isn't clean, try this diagnostic:

```powershell
# Diagnostic script - save as diagnose_version.ps1
Write-Host "🔍 Version Diagnostic" -ForegroundColor Cyan

# Check Git status
Write-Host "`nGit Status:" -ForegroundColor Yellow
git status --short
git describe --tags --exact-match

# Check setuptools_scm version detection
Write-Host "`nsetuptools_scm Version Detection:" -ForegroundColor Yellow
python -c "
try:
    import setuptools_scm
    version = setuptools_scm.get_version()
    print(f'Detected version: {version}')
except Exception as e:
    print(f'Error: {e}')
"

# Check if _version.py is created during build
Write-Host "`nChecking _version.py:" -ForegroundColor Yellow
if (Test-Path "src/x_zic/_version.py") {
    Get-Content "src/x_zic/_version.py"
} else {
    Write-Host "❌ _version.py not found" -ForegroundColor Red
}

# Build and check result
Write-Host "`nBuilding package..." -ForegroundColor Yellow
python -m build
Get-ChildItem dist/
```

Run the diagnostic:
```powershell
.\diagnose_version.ps1
```

## 9. Quick Manual Process for Now

Since you're already set up, let's complete the process manually:

```powershell
# You've already pushed main, now create and push the tag:
git tag -a v0.1.5 -m "Release version 0.1.5 - Dynamic versioning"
git push origin v0.1.5

# Switch to the tagged commit and build
git checkout v0.1.5
python clean_build_dirs.py
python -m build

# Verify
pip install --force-reinstall dist/x_zic-0.1.5-py3-none-any.whl
python -c "import x_zic; print(f'Version: {x_zic.__version__}')"

# Go back to main for development
git checkout main
```

## 10. For Future Reference - PowerShell vs Bash

| Bash Command | PowerShell Equivalent |
|-------------|---------------------|
| `cmd1 || cmd2` | `cmd1; if ($LASTEXITCODE -ne 0) { cmd2 }` |
| `2>/dev/null` | `2>$null` |
| `ls -la` | `Get-ChildItem` or `ls` |
| `cat file` | `Get-Content file` |
| `rm file` | `Remove-Item file` |

The key points:
- Use `;` instead of `||` in PowerShell
- Use `2>$null` instead of `2>/dev/null`
- Most Git commands work the same

Run the manual process above and let me know what version output you get!