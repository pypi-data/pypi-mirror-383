



















7. Verify Everything Works
bash
# Complete test sequence
git checkout v0.1.5
python clean_build_dirs.py
python -m build

# Check the built files
twine check dist/*

# Test installation
pip install --force-reinstall dist/x_zic-0.1.5-py3-none-any.whl

# Final verification
python -c "
import x_zic
print(f'Package: {x_zic.__name__}')
print(f'Version: {x_zic.__version__}')
print(f'Location: {x_zic.__file__}')
"

# Should output:
# Package: x_zic
# Version: 0.1.5
# Location: .../x_zic/__init__.py

I can see several issues in your build process. Let me help you fix them step by step:

## 1. Fix Line Ending Warnings (CRLF → LF)

The warnings about CRLF being replaced by LF are normal on Windows. You can configure Git to handle this properly:

```bash
# Configure Git to handle line endings properly
git config --global core.autocrlf true

# Or for this repository only
git config core.autocrlf true

# Add and commit again (warnings are normal on Windows)
git add .
git commit -m "Fix: license headers"
```

## 2. Fix Version Number Issues

The main problem is your version number format. You're getting `0.1.5.post0+g9be8f185e.d20251010` instead of a clean `0.1.5`. Here's how to fix it:

### Update `pyproject.toml` with proper version configuration:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[project]
name = "x-zic"
dynamic = ["version"]
description = "High-performance Python parser for IANA Time Zone Database with smart caching"
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
license = "GPL-3.0-or-later"
keywords = ["timezone", "tzdb", "iana", "parser", "dst", "time"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Software Development :: Libraries",
    "Topic :: System :: Time",
]
requires-python = ">=3.8"
dependencies = []

[project.urls]
Homepage = "https://github.com/mlotfic/x-zic"
Documentation = "https://x-zic.readthedocs.io"
Repository = "https://github.com/mlotfic/x-zic"
"Bug Tracker" = "https://github.com/mlotfic/x-zic/issues"

[project.optional-dependencies]
pandas = ["pandas>=1.3.0"]
analysis = ["pandas>=1.3.0", "numpy>=1.20.0"]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.0",
    "black>=21.0",
    "isort>=5.0",
    "mypy>=0.900",
    "flake8>=3.9",
    "pre-commit>=2.15",
]
docs = [
    "sphinx>=5.0",
    "sphinx-rtd-theme>=1.0",
    "myst-parser>=0.15",
    "sphinx-copybutton>=0.3",
]

[tool.setuptools_scm]
write_to = "src/x_zic/_version.py"
write_to_template = "__version__ = '{version}'"
version_scheme = "release-branch-semver"
local_scheme = "node-and-date"

[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

## 3. Create a Clean Tag and Build

Here are the steps to get a clean build:

### Step 1: Delete the problematic tag and create a new one

```bash
# Delete the existing tag
git tag -d v0.1.5
git push origin --delete v0.1.5

# Make sure you're on a clean state
git status

# Create a proper annotated tag
git tag -a v0.1.5 -m "Release version 0.1.5 - GPLv3 license"

# Push the tag
git push origin v0.1.5
```

### Step 2: Clean and rebuild

```bash
# Clean everything
python clean_build_dirs.py

# Make sure you're on the main branch and up to date
git checkout main
git pull origin main

# Build with clean environment
python -m build --no-isolation
```
# Clean build directories
python clean_build_dirs.py

# Remove old tags
git tag -d v0.1.5 2>/dev/null || true
git push origin --delete v0.1.5 2>/dev/null || true

# Make sure we're on main and up to date
git checkout main
git pull origin main

# Add the new files
git add .
git commit -m "Setup: dynamic versioning with setuptools_scm"
git push origin main


8. Verify Clean Build
After building, check the distribution:

bash
# List built files
ls -la dist/

# Check the metadata
python -m twine check dist/*

# Test installation
pip install --force-reinstall dist/x_zic-0.1.5-py3-none-any.whl

# Verify
python -c "import x_zic; print(f'Success! Version: {x_zic.__version__}')"
```bash
# Step 1: Remove problematic files
python clean_build_dirs.py
rm setup.py 2>/dev/null || true
rm src/x_zic/_version.py 2>/dev/null || true

# Step 2: Update files with the new configurations above
# Copy the pyproject.toml, src/x_zic/__init__.py, and MANIFEST.in content above

# Step 3: Commit changes
git add .
git commit -m "Clean build: static versioning and modern configuration"

# Step 4: Delete old tag and create new one
git tag -d v0.1.5 2>/dev/null || true
git push origin --delete v0.1.5 2>/dev/null || true

git tag -a v0.1.5 -m "Release version 0.1.5 - Clean build"
git push origin main --tags

# Step 5: Clean build with no warnings
python -m build --no-isolation
```

## 5. Complete Clean Build Process

```bash
# Step 1: Clean everything
python clean_build_dirs.py

# Step 2: Remove old tag if exists
git tag -d v0.1.5 2>/dev/null || true
git push origin --delete v0.1.5 2>/dev/null || true

# Step 3: Update files with static version
# Update pyproject.toml and src/x_zic/__init__.py as shown above

# Step 4: Commit changes
git add .
git commit -m "Release v0.1.5: GPLv3 license and static version"

# Step 5: Create and push tag
git tag -a v0.1.5 -m "Release version 0.1.5"
git push origin main --tags

# Step 6: Build with clean environment
python -m build --no-isolation

# Step 7: Verify the build
ls -la dist/
```

## 6. Check the Built Package

```bash
# Check what was built
twine check dist/*

# Test install locally
pip install dist/x_zic-0.1.5-py3-none-any.whl

# Verify installation
python -c "import x_zic; print(f'Version: {x_zic.__version__}')"
```

## 7. If You Want to Keep Dynamic Versioning

If you prefer dynamic versioning, make sure:

1. **You have a `.git` directory** (the build needs Git history)
2. **You're on a tagged commit** when building
3. **Use the correct setuptools_scm configuration**

```bash
# Make sure you're on a tagged commit
git checkout v0.1.5

# Build from the tagged commit
python -m build
```

---

# 🚀 **x-zic PyPI Release Workflow**

Use this **every time you add code and want a clean PyPI build**.

---

## 🧭 1️⃣ Prepare Your Workspace

Run these in the project root (`E:\GitHub\date-toolkit\x-zic`):

```bash
git pull origin main
```

Confirm you’re up-to-date and on the right branch.

---

## 🧹 2️⃣ Clean the Build Environment

```bash
python clean_build_dirs.py
```

(optional but smart)

```bash
pip uninstall -y x-zic
```

---

## 🧩 3️⃣ Commit Your Changes

Add any new files or edits:

```bash
git add .
git commit -m "Update: <short summary of your change>"
```

---

## 🏷️ 4️⃣ Bump Version (with Tag)

Decide your next version — e.g. `0.1.3`.

```bash
git tag -d v0.1.4
git tag v0.1.4
```

> 💡 **Tip:** Use semantic versioning
>
> * Bug fix → `0.1.3`
> * New feature → `0.2.0`
> * Major rewrite → `1.0.0`

---

## 🛠️ 5️⃣ Build the Package

```bash
python -m build
```

✅ You should see:

```
dist/
├── x_zic-0.1.3.tar.gz
└── x_zic-0.1.3-py3-none-any.whl
```

If you see `+dirty` → commit all changes and rebuild.

---

## 🔐 6️⃣ Upload to PyPI

```bash
python -m twine upload dist/*
```

You’ll see:

```
Uploading x_zic-0.1.3-py3-none-any.whl
100% ━━━━━━━━━━━━━━━━━━━━━━━━
```

If your `.pypirc` and API token are set up, no password prompt will appear.

---

## 🧾 7️⃣ Verify Installation

After uploading, test your release:

```bash
pip install --upgrade x-zic
python -c "import x_zic; print(x_zic.__version__)"
```

✅ Should print:

```
0.1.3
```

---

## 🔁 8️⃣ Push Everything to GitHub

```bash
git push origin main --tags
```

---

## 🎯 TL;DR — Quick Command Sequence

```bash
git pull
git add .
git commit -m "Update"
git tag v0.1.3
Remove-Item -Recurse -Force dist, build, src\x_zic.egg-info
python -m build
python -m twine upload dist/*
git push origin main --tags
```

---

## 🧰 (Optional) Automate it

You can create a PowerShell script `release.ps1` inside your project:

```powershell
param([string]$version)

git pull
git add .
git commit -m "Release version $version"
git tag "v$version"

Remove-Item -Recurse -Force dist, build, src\x_zic.egg-info -ErrorAction SilentlyContinue

python -m build
python -m twine upload dist/*

git push origin main --tags
```

Run it like:

```bash
./release.ps1 0.1.3
```

---

Would you like me to make that PowerShell script (`release.ps1`) ready-to-drop into your repo — including safety checks (e.g., uncommitted files, version confirmation)? It’ll make your PyPI releases one-liner easy.
