Excellent — time to make this smooth and repeatable like a pro release pipeline.
Here’s your **bulletproof “release-to-PyPI” playbook** for your `x-zic` project.

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
git tag v0.1.3
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
