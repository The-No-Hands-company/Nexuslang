# NLPL Editor Integrations

This directory contains editor plugins and IDE extensions for NLPL.

| Editor | Location | Status |
|--------|----------|--------|
| Neovim | `neovim/` | Complete |
| Emacs | `emacs/` | Complete |
| Sublime Text | `sublime-text/` | Complete |
| IntelliJ IDEA (and JetBrains IDEs) | `intellij/` | Complete |
| VS Code | `../vscode-extension/` | Separate directory |

## Quick Install

### Neovim (lazy.nvim)
```lua
{
  dir = "path/to/NLPL/editors/neovim",
  config = function()
    require("nlpl").setup()
  end
}
```

### Emacs
```elisp
(load "path/to/NLPL/editors/emacs/nlpl-mode.el")
```

### Sublime Text
Copy `sublime-text/NLPL/` into your Sublime Text `Packages/` directory.

### IntelliJ IDEA
Build with `./gradlew buildPlugin` and install from disk, or wait for the JetBrains Marketplace release.

All integrations connect to the NLPL language server (`nlpl lsp`) for:
- Code completion
- Go-to-definition
- Find references
- Hover documentation
- Inline diagnostics
- Signature help
