# NLPL Distribution Summary

Complete overview of how NLPL can be used and distributed.

## 🎯 Current Status (January 5, 2026)

### ✅ What's Ready Now

1. **VSCode Extension** - Fully functional, workspace-ready
2. **LSP Server** - Complete with all features
3. **CLI Interpreter** - Works via `python3 src/main.py`
4. **Documentation** - Comprehensive guides for deployment
5. **Installation Scripts** - Automated setup tools

### 🚧 What's Coming Next

1. **VSCode Marketplace** - Pending publisher account
2. **PyPI Package** - Pending `pip install nlpl`
3. **Binary Distributions** - Standalone executables
4. **Package Managers** - Homebrew, APT, etc.

---

## 📦 Using NLPL Extension

### In Your Current Project (This Repo)

**Already set up!** Just reload VSCode:

```bash
# Reload VSCode window
Ctrl+Shift+P → "Developer: Reload Window"

# Open any .nlpl file
code examples/01_basic_concepts.nlpl
```

**Features available:**
- ✅ Syntax highlighting
- ✅ Real-time diagnostics
- ✅ Auto-completion (Ctrl+Space)
- ✅ Signature help (parameter hints)
- ✅ Code actions (quick fixes)
- ✅ Go-to-definition (F12)
- ✅ Hover information

### In Other Projects

**Option 1: Global Installation (Recommended)**

```bash
# Run from NLPL repository
./install_extension_globally.sh

# Extension now works in ALL projects!
```

**Configuration for new projects** (`.vscode/settings.json`):
```json
{
  "nlpl.languageServer.enabled": true,
  "nlpl.languageServer.path": "/path/to/NLPL/src/nlpl_lsp.py"
}
```

**Option 2: Copy Extension to Project**

```bash
# In your new project
mkdir -p .vscode/extensions
cp -r /path/to/NLPL/.vscode/extensions/nlpl .vscode/extensions/

# Copy settings
cp /path/to/NLPL/.vscode/settings.json .vscode/
```

**Option 3: Package and Install**

```bash
# From NLPL repository
./package_extension.sh

# Installs: nlpl-language-support-0.1.0.vsix
code --install-extension nlpl-language-support-0.1.0.vsix
```

---

## 🚀 Deploying NLPL for Production

### Step 1: Publish to VSCode Marketplace

**Prerequisites:**
```bash
# Install vsce (VSCode Extension CLI)
npm install -g @vscode/vsce
```

**Setup:**
1. Create publisher account: https://marketplace.visualstudio.com/manage
2. Generate Azure DevOps Personal Access Token
3. Login: `vsce login <publisher-name>`

**Publish:**
```bash
cd .vscode/extensions/nlpl
vsce package  # Creates .vsix
vsce publish  # Publishes to marketplace
```

**Users install with:**
```bash
code --install-extension nlpl-lang.nlpl-language-support
# Or search "NLPL" in VSCode Extensions
```

### Step 2: Publish to PyPI

**Setup `pyproject.toml`:**
```toml
[project]
name = "nlpl"
version = "1.0.0"
description = "Natural Language Programming Language"
authors = [{name = "NLPL Team"}]
dependencies = [...]

[project.scripts]
nlpl = "nlpl.main:main"
nlpl-lsp = "nlpl.lsp.server:main"
```

**Publish:**
```bash
python -m build
twine upload dist/*
```

**Users install with:**
```bash
pip install nlpl
nlpl run hello.nlpl
```

### Step 3: Other Editors

**Neovim/Vim (LSP):**
```lua
-- ~/.config/nvim/lua/nlpl.lua
local lspconfig = require('lspconfig')
lspconfig.nlpl.setup{
  cmd = {'python3', '/path/to/nlpl_lsp.py'},
  filetypes = {'nlpl'}
}
```

**Sublime Text:**
```json
{
  "clients": {
    "nlpl": {
      "command": ["python3", "/path/to/nlpl_lsp.py"],
      "selector": "source.nlpl"
    }
  }
}
```

**Emacs:**
```elisp
(lsp-register-client
 (make-lsp-client
  :new-connection (lsp-stdio-connection
                   '("python3" "/path/to/nlpl_lsp.py"))
  :major-modes '(nlpl-mode)
  :server-id 'nlpl-lsp))
```

### Step 4: Package Managers

**Homebrew Formula:**
```ruby
class Nlpl < Formula
  desc "Natural Language Programming Language"
  homepage "https://github.com/Zajfan/NLPL"
  url "https://github.com/Zajfan/NLPL/archive/v1.0.0.tar.gz"
  
  depends_on "python@3.11"
  
  def install
    virtualenv_install_with_resources
  end
end
```

**Install:**
```bash
brew tap nlpl-lang/nlpl
brew install nlpl
```

---

## 📝 Configuration Examples

### Workspace Configuration (`.vscode/settings.json`)

**Basic:**
```json
{
  "nlpl.languageServer.enabled": true,
  "nlpl.languageServer.path": "${workspaceFolder}/src/nlpl_lsp.py"
}
```

**With Debugging:**
```json
{
  "nlpl.languageServer.enabled": true,
  "nlpl.languageServer.path": "${workspaceFolder}/src/nlpl_lsp.py",
  "nlpl.trace.server": "verbose"
}
```

**Custom Installation:**
```json
{
  "nlpl.languageServer.enabled": true,
  "nlpl.languageServer.path": "/usr/local/bin/nlpl-lsp",
  "nlpl.trace.server": "off",
  "files.associations": {
    "*.nlpl": "nlpl"
  }
}
```

---

## 🎓 Example: Setting Up a New NLPL Project

### From Scratch

```bash
# 1. Create project directory
mkdir my-nlpl-app
cd my-nlpl-app

# 2. Install NLPL globally (one-time)
/path/to/NLPL/install_extension_globally.sh

# 3. Configure workspace
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
  "nlpl.languageServer.enabled": true,
  "nlpl.languageServer.path": "/path/to/NLPL/src/nlpl_lsp.py"
}
EOF

# 4. Create your first file
cat > main.nlpl << 'EOF'
# main.nlpl - My first NLPL app

function main
    print text "Hello from my NLPL app!"

call main
EOF

# 5. Open in VSCode
code .

# 6. Run your program
python3 /path/to/NLPL/src/main.py main.nlpl
```

### From Template (Future)

```bash
# Once NLPL is on PyPI
pip install nlpl

# Create new project
nlpl new my-project
cd my-project

# Files created:
# - main.nlpl (entry point)
# - README.md
# - .vscode/settings.json (pre-configured)
# - tests/ (test directory)

# Run
nlpl run main.nlpl
```

---

## 🔧 Development Workflow

### For NLPL Contributors

```bash
# 1. Clone repository
git clone https://github.com/Zajfan/NLPL.git
cd NLPL

# 2. Install development dependencies
pip install -e ".[dev]"

# 3. Install extension locally
./install_extension_globally.sh

# 4. Make changes to LSP server or extension

# 5. Test changes
pytest tests/
./package_extension.sh  # Test packaging

# 6. Reload VSCode to test extension
# Ctrl+Shift+P → "Developer: Reload Window"
```

### For NLPL Users

```bash
# 1. Install NLPL
pip install nlpl  # (Future - once on PyPI)

# 2. Install VSCode extension
code --install-extension nlpl-lang.nlpl-language-support

# 3. Create NLPL files
echo 'print text "Hello!"' > hello.nlpl

# 4. Run
nlpl run hello.nlpl

# 5. Develop with full IDE support!
```

---

## 📊 Distribution Roadmap

### Phase 1: Local Development (✅ Complete)
- ✅ Extension works in this repository
- ✅ Manual installation scripts
- ✅ Documentation complete

### Phase 2: Public Release (🚧 In Progress)
- 🔲 Register VSCode publisher account
- 🔲 Publish to VSCode Marketplace
- 🔲 Create PyPI package
- 🔲 GitHub Releases with binaries
- 🔲 Basic documentation website

### Phase 3: Package Managers (📅 Planned)
- 🔲 Homebrew formula
- 🔲 APT repository (Ubuntu/Debian)
- 🔲 Chocolatey package (Windows)
- 🔲 Snap package (Linux)
- 🔲 Docker Hub images

### Phase 4: Ecosystem (📅 Future)
- 🔲 JetBrains plugin (IntelliJ, PyCharm)
- 🔲 Online playground/REPL
- 🔲 Language server in multiple languages (Rust, Go)
- 🔲 Native compiler (LLVM backend)
- 🔲 Package registry (like npm, PyPI)

---

## 🆘 Quick Troubleshooting

### Extension not working?

**Check 1: Language Server Running**
```bash
# View output
View → Output → "NLPL Language Server"

# Should see: "NLPL Language Server started"
```

**Check 2: Python Version**
```bash
python3 --version  # Must be 3.11+
```

**Check 3: File Extension**
```bash
# Ensure file ends with .nlpl
mv myfile myfile.nlpl
```

**Check 4: Reload VSCode**
```bash
Ctrl+Shift+P → "Developer: Reload Window"
```

### No auto-completion?

**Solution 1: Manual Trigger**
```bash
Type code and press: Ctrl+Space
```

**Solution 2: Check Language Mode**
```bash
# Bottom-right corner should show: "NLPL"
# If not, click and select "NLPL"
```

**Solution 3: Check for Errors**
```bash
# Open Problems panel
Ctrl+Shift+M

# Fix any syntax errors
```

---

## 📚 Resources

### Documentation
- **Quick Start:** `QUICK_START.md` (5-minute tutorial)
- **Deployment Guide:** `DEPLOYMENT_GUIDE.md` (complete publishing guide)
- **Extension Guide:** `VSCODE_EXTENSION_GUIDE.md` (detailed features)
- **Language Docs:** `docs/` directory (44+ documents)
- **Examples:** `examples/` directory (25+ programs)

### Installation Scripts
- **Global Install:** `install_extension_globally.sh`
- **Package Extension:** `package_extension.sh`
- **Setup Extension:** `setup_vscode_extension.sh`

### Support
- **Issues:** https://github.com/Zajfan/NLPL/issues
- **Discussions:** https://github.com/Zajfan/NLPL/discussions
- **Repository:** https://github.com/Zajfan/NLPL

---

## 🎯 Summary

### What Works Today

✅ **VSCode Extension** - Fully functional in workspace and globally  
✅ **LSP Features** - Diagnostics, completion, signature help, code actions  
✅ **Installation Scripts** - Automated setup and packaging  
✅ **Documentation** - Complete guides for all use cases  
✅ **Multi-Editor Support** - Configuration examples for 5+ editors  

### How to Use

**In this project:**
```bash
Ctrl+Shift+P → Reload Window
```

**In other projects:**
```bash
./install_extension_globally.sh
```

**Distribute to users:**
```bash
./package_extension.sh
# Share the .vsix file
```

### Next Steps

1. **Immediate:** Test extension in other projects
2. **Short-term:** Publish to VSCode Marketplace
3. **Medium-term:** Create PyPI package
4. **Long-term:** Full ecosystem (package managers, other editors)

---

**NLPL is ready for development and distribution!** 🚀
