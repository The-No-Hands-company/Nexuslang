# LSP Testing and Completion Guide - Week 1

**Date Started:** February 17, 2026  
**Status:** IN PROGRESS  
**Goal:** Complete LSP testing and fix critical issues in 2-3 weeks

---

## Current Status (Day 1 - February 17)

### ✅ What's Working

1. **LSP Server Infrastructure** (5420 lines of code!)
   - server.py (906 lines) - Main server with full LSP protocol
   - completions.py (327 lines) - Auto-completion
   - definitions.py (364 lines) - Go-to-definition
   - hover.py (316 lines) - Hover information
   - diagnostics.py (520 lines) - Error detection
   - references.py (463 lines) - Find references
   - rename.py (588 lines) - Rename refactoring
   - code_actions.py (309 lines) - Quick fixes
   - signature_help.py (221 lines) - Parameter hints
   - formatter.py (289 lines) - Code formatting
   - symbols.py (330 lines) - Symbol search
   - workspace_index.py (577 lines) - Workspace indexing
   - semantic_tokens.py (210 lines) - Syntax highlighting

2. **Server Initialization** ✅
   - Starts correctly via stdio and TCP
   - Handles LSP handshake properly
   - Reports all capabilities correctly
   - Shuts down cleanly

3. **VS Code Extension** ✅
   - Package.json configured
   - Language configuration exists
   - Debugger integration complete
   - LSP client configuration ready

### ⚠️ What Needs Testing

1. **Go-to-Definition**
   - Same-file navigation - needs testing
   - Cross-file navigation - CRITICAL, likely incomplete
   - Import resolution - needs verification

2. **Auto-Completion**
   - Keyword completion - needs testing
   - Context-aware completions - needs testing
   - Stdlib function completion - needs testing

3. **Diagnostics**
   - Syntax errors - needs testing
   - Type errors - needs testing
   - Import errors - needs testing

4. **Other Features**
   - Find references - needs testing
   - Rename refactoring - needs testing
   - Hover information - needs testing
   - Code actions - needs testing
   - Signature help - needs testing

---

## Week 1 Plan (Feb 17-23): Manual Testing & Critical Fixes

### Day 1-2 (Feb 17-18): Setup & Manual Testing

**Tasks:**

1. ✅ Verify LSP server starts correctly
2. ✅ Check LSP code exists and is substantial (5420 lines!)
3. ⏳ Install/update VS Code extension
4. ⏳ Test in VS Code manually:
   - Open NLPL file
   - Check if errors appear
   - Try autocomplete (Ctrl+Space)
   - Try go-to-definition (F12)
   - Try find references (Shift+F12)
   - Try rename (F2)
   - Try hover (mouse over symbols)

**How to Install Extension:**

```bash
cd vscode-extension
npm install
npm run compile
code --install-extension nlpl-language-support-0.1.0.vsix
# OR
vsce package
code --install-extension nlpl-language-support-0.1.0.vsix
```

**Manual Test Checklist:**

- [ ] Open `examples/01_basic_concepts.nlpl` in VS Code
- [ ] Check if syntax highlighting works
- [ ] Introduce a syntax error - does it show red squiggle?
- [ ] Type `function` - does autocomplete work?
- [ ] F12 on a function call - does go-to-definition work?
- [ ] Shift+F12 on a function - does find references work?
- [ ] F2 on a variable - does rename work?
- [ ] Hover over a function - does documentation appear?
- [ ] Ctrl+Shift+I - does formatting work?

### Day 3-4 (Feb 19-20): Fix Critical Issues

Based on manual testing, fix the top 3 most broken features.

**Priority Order:**

1. **Cross-file go-to-definition** (if broken)
   - Check workspace_index.py
   - Verify import resolution
   - Test with test_module_a.nlpl and test_module_b.nlpl

2. **Diagnostics** (if not showing)
   - Check diagnostics.py integration
   - Verify parser errors are surfaced
   - Test with intentionally broken code

3. **Auto-completion** (if not working)
   - Check completions.py triggers
   - Verify stdlib functions appear
   - Test context-awareness

### Day 5 (Feb 21): Documentation

1. Write LSP User Guide:
   - Installation instructions
   - Feature overview with screenshots
   - Keyboard shortcuts reference
   - Troubleshooting common issues

2. Update VS Code extension README

### Day 6-7 (Feb 22-23): Performance & Polish

1. Test with large files (1000+ lines)
2. Measure latency for completions, go-to-definition
3. Optimize if needed
4. Fix any remaining bugs from manual testing

---

## Week 2 Plan (Feb 24-Mar 2): Refactoring & Advanced Features

### Tasks:

1. **Refactoring Operations**
   - Extract function refactoring
   - Inline variable refactoring
   - Change signature refactoring

2. **Improved Code Actions**
   - Auto-fix common errors
   - Import organization
   - Remove unused variables

3. **Completion Improvements**
   - Method call completions
   - Import completions
   - Parameter completions

---

## Week 3 Plan (Mar 3-9): Testing & Documentation

### Tasks:

1. **Automated Test Suite**
   - Unit tests for each LSP provider
   - Integration tests simulating VS Code
   - Performance benchmarks

2. **Final Documentation**
   - Developer guide (how LSP works)
   - Architecture diagrams
   - API reference

3. **Demo Video**
   - 5-minute screencast
   - Show all major features
   - Upload to project docs

---

## Success Criteria

By March 9, 2026:

- ✅ LSP works seamlessly in VS Code
- ✅ Go-to-definition works cross-file
- ✅ Auto-completion is helpful and accurate
- ✅ Diagnostics show errors immediately
- ✅ Refactoring operations work reliably
- ✅ Performance is <500ms for all operations
- ✅ Documentation is complete
- ✅ Demo video created

---

## Known Issues & Workarounds

### Issue 1: Test Script Hangs

**Problem:** `test_lsp_goto_definition.py` hangs when reading LSP responses

**Likely Cause:** LSP server not flushing stdout or buffering issue

**Workaround:** Use manual testing in VS Code instead of programmatic tests

**Fix:** Add `sys.stdout.flush()` after each JSON-RPC response in server.py

### Issue 2: Cross-File Navigation Unknown

**Problem:** Haven't verified if cross-file go-to-definition works

**Status:** Need to test manually in VS Code with test_module_a/b.nlpl

**Priority:** CRITICAL - test this first tomorrow

---

## Next Steps (Tomorrow - Feb 18)

1. Install/update VS Code extension
2. Open test files in VS Code
3. Run through manual test checklist
4. Document what works and what doesn't
5. Create GitHub issue for each broken feature
6. Start fixing the most critical issue (likely cross-file nav)

---

## Notes

- LSP code is substantial (5420 lines) - this is GOOD news!
- Server initialization works perfectly
- Main work is testing and fixing bugs, not writing from scratch
- Should be able to complete in 2-3 weeks as estimated
