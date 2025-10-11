# Publishing jhadoo to PyPI

This guide walks you through publishing your package to PyPI (Python Package Index).

## Prerequisites

1. **Create PyPI Account**
   - Go to https://pypi.org/account/register/
   - Create an account and verify your email

2. **Create TestPyPI Account** (recommended for testing)
   - Go to https://test.pypi.org/account/register/
   - Create a separate account for testing

3. **Install Build Tools**
   ```bash
   pip install --upgrade pip
   pip install --upgrade build twine
   ```

## Pre-Publishing Checklist

Before publishing, update these files:

### 1. Update `setup.py` and `pyproject.toml`
- [ ] Set your email in `author_email`
- [ ] Update GitHub URL in `url` and `project_urls`
- [ ] Verify version number is correct

### 2. Update `README.md`
- [ ] Replace placeholder URLs with your actual repository
- [ ] Add screenshots if desired
- [ ] Test all example commands

### 3. Test Locally
```bash
# Install in development mode
pip install -e .

# Run tests
pytest

# Test the CLI
jhadoo --dry-run
jhadoo --dashboard
jhadoo --generate-config
```

## Publishing Steps

### Step 1: Clean Previous Builds
```bash
rm -rf build/ dist/ *.egg-info
```

### Step 2: Build the Package
```bash
python -m build
```

This creates:
- `dist/jhadoo-1.0.0.tar.gz` (source distribution)
- `dist/jhadoo-1.0.0-py3-none-any.whl` (wheel distribution)

### Step 3: Test on TestPyPI (Recommended)
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your-testpypi-token>

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ jhadoo
```

### Step 4: Publish to PyPI
```bash
# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: <your-pypi-token>
```

### Step 5: Verify Installation
```bash
# Install from PyPI
pip install jhadoo

# Test it works
jhadoo --version
jhadoo --help
```

## Using API Tokens (Recommended)

Instead of passwords, use API tokens for better security.

### Create PyPI Token
1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Set scope to "Entire account" or specific project
4. Copy the token (starts with `pypi-`)

### Create TestPyPI Token
1. Go to https://test.pypi.org/manage/account/token/
2. Follow same steps as above

### Configure `.pypirc` (Optional)
Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
```

Then upload without prompts:
```bash
twine upload dist/*
twine upload --repository testpypi dist/*
```

## Version Management

### Update Version Number
Update in these files:
- `setup.py` → `version="1.0.1"`
- `setup.cfg` → `version = 1.0.1`
- `pyproject.toml` → `version = "1.0.1"`
- `jhadoo/__init__.py` → `__version__ = "1.0.1"`

### Semantic Versioning
- **MAJOR** (1.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.1): Bug fixes

## Publishing Updates

```bash
# 1. Update version numbers in all files
# 2. Update CHANGELOG (if you create one)
# 3. Commit changes
git add .
git commit -m "Release v1.0.1"
git tag v1.0.1
git push origin main --tags

# 4. Clean and rebuild
rm -rf build/ dist/ *.egg-info
python -m build

# 5. Upload
twine upload dist/*
```

## Troubleshooting

### Error: "File already exists"
You can't upload the same version twice. Increment the version number.

### Error: "Invalid distribution"
Run checks before uploading:
```bash
twine check dist/*
```

### Error: "Package name already taken"
Choose a different package name. Check availability:
```bash
pip search jhadoo  # or check pypi.org
```

### Testing Build Locally
```bash
# Install from local wheel
pip install dist/jhadoo-1.0.0-py3-none-any.whl

# Or install from source distribution
pip install dist/jhadoo-1.0.0.tar.gz
```

## Post-Publishing

### 1. Add PyPI Badge to README
```markdown
[![PyPI version](https://badge.fury.io/py/jhadoo.svg)](https://badge.fury.io/py/jhadoo)
```

### 2. Monitor Downloads
- Check https://pypistats.org/packages/jhadoo
- View package page: https://pypi.org/project/jhadoo/

### 3. Update Documentation
- Link to PyPI page in your GitHub README
- Update installation instructions
- Add CHANGELOG.md for version history

## Security Best Practices

1. **Never commit `.pypirc` to git**
   - Already in `.gitignore`

2. **Use API tokens, not passwords**
   - More secure and can be revoked

3. **Enable 2FA on PyPI**
   - Adds extra security to your account

4. **Review code before publishing**
   - Can't unpublish versions easily

## Resources

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- TestPyPI: https://test.pypi.org/
- Twine Docs: https://twine.readthedocs.io/

---

Good luck with your package! 🚀


