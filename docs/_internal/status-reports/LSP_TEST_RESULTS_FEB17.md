# LSP Manual Testing Results - February 17, 2026

**Extension:** nlpl-language-support-0.1.0.vsix  
**Test Environment:** VS Code on Linux  
**Test File:** examples/01_basic_concepts.nlpl, test_programs/lsp_tests/test_module_a.nlpl

---

## Summary

**Working:** 2/10 features (20%)  
**Broken:** 4 features (40%)  
**Not Tested Yet:** 4 features (40%)

### ✅ Working Features

1. **Syntax Highlighting** - TextMate grammar working perfectly
2. **Auto-Completion** (`Ctrl+Space`) - Keyword suggestions work
3. **Go-to-Definition** (`F12`) - Jumps to function/class definitions

### ❌ Broken Features (Priority Order)

1. **🔴 HIGH: Diagnostics** - No error squiggles appear for invalid syntax
   - Test: Added `function bad` (invalid syntax)
   - Expected: Red squiggle with error message
   - Actual: No visual feedback at all
   - Impact: Users can't see syntax errors in real-time

2. **🔴 HIGH: Hover Documentation** - No tooltips when hovering over symbols
   - Test: Hovered over function names
   - Expected: Tooltip with signature/docstring
   - Actual: Nothing appears
   - Impact: Users can't quickly see function signatures

3. **🟡 MEDIUM: Find References** (`Shift+F12`) - Doesn't show references panel
   - Test: Used Shift+F12 on function name
   - Expected: Panel showing all usages
   - Actual: Nothing happens
   - Impact: Hard to understand code usage

4. **🟡 MEDIUM: Rename Refactoring** (`F2`) - Rename dialog doesn't appear
   - Test: Pressed F2 on variable name
   - Expected: Rename dialog with preview
   - Actual: Nothing happens
   - Impact: Manual refactoring required

### 🔷 Not Tested Yet

- Code Actions (Quick fixes)
- Signature Help (Parameter hints)
- Formatting
- Cross-file Go-to-Definition

---

## Detailed Test Results

### 1. Syntax Highlighting ✅

**Test:** Open .nlpl file  
**Result:** Keywords, strings, comments properly colored  
**Status:** Working

### 2. Diagnostics ❌ HIGH PRIORITY

**Test:**
```nlpl
function bad  # Invalid - missing 'called' or 'with'
```

**Expected:** Red squiggle under `function bad`  
**Actual:** No error indication at all  
**Root Cause:** Diagnostics provider not publishing to VS Code  

**Fix Strategy:**
- Check if `diagnostics.py` is being called
- Verify `textDocument/publishDiagnostics` is sent
- Add logging to see what diagnostics are generated
- Test with `server.py --debug` mode

### 3. Auto-Completion ✅

**Test:** Type `func` + `Ctrl+Space`  
**Result:** Shows `function`, `for each`, and other keywords  
**Status:** Working perfectly

### 4. Go-to-Definition ✅

**Test:** F12 on function call  
**Result:** Jumps to function definition  
**Status:** Working perfectly

### 5. Find References ❌ MEDIUM PRIORITY

**Test:** Shift+F12 on `greet` function  
**Expected:** Panel showing all calls to `greet`  
**Actual:** No references panel appears  

**Fix Strategy:**
- Check if `references.py` is returning results
- Verify LSP response format matches spec
- Test with VS Code LSP inspector

### 6. Rename Refactoring ❌ MEDIUM PRIORITY

**Test:** F2 on variable name  
**Expected:** Rename dialog with live preview  
**Actual:** Nothing happens  

**Fix Strategy:**
- Check `rename.py` provider implementation
- Verify `textDocument/rename` request handler
- Test `prepareRename` capability

### 7. Hover Documentation ❌ HIGH PRIORITY

**Test:** Mouse over `greet` function  
**Expected:** Tooltip: `function greet with name as String returns String`  
**Actual:** No tooltip appears  

**Fix Strategy:**
- Check `hover.py` provider
- Verify hover response format (Markup vs plain text)
- Add debug logging to see if hover is even called
- Test with simple static hover first

### 8-10. Not Yet Tested

- **Code Actions:** Quick fixes (lightbulb icon)
- **Signature Help:** Parameter hints while typing function calls
- **Formatting:** Document/range formatting

---

## Root Cause Analysis

### Why Some Features Work and Others Don't

**Working features (Completion, Go-to-Definition):**
- These were probably tested during initial LSP development
- Simple request/response pattern
- No complex state management

**Broken features (Diagnostics, Hover, References, Rename):**
- May have never been manually tested in VS Code
- Could have incorrect LSP response format
- Might not be registered in server capabilities properly
- Could be silently failing (no error messages)

### Key Questions to Answer

1. **Is the server receiving these requests?**
   - Enable `--debug` mode
   - Check `/tmp/nlpl-lsp.log` for incoming requests
   
2. **Is the provider returning data?**
   - Add print statements in hover.py, diagnostics.py, etc.
   - Check if methods are even being called

3. **Is the response format correct?**
   - LSP spec requires specific JSON structures
   - VS Code silently ignores malformed responses

---

## Top 3 Priorities to Fix

### Priority 1: Diagnostics (Est: 2-3 hours)

**Why critical:** Users need immediate syntax error feedback

**Fix approach:**
1. Add logging to `diagnostics.py`
2. Verify diagnostics are generated for syntax errors
3. Check `publishDiagnostics` notification format
4. Test with intentional syntax errors
5. Ensure diagnostics update on file save

**Success criteria:**
- Red squiggles appear for invalid syntax
- Hover over squiggle shows error message
- Diagnostics clear when error fixed

### Priority 2: Hover Documentation (Est: 2-3 hours)

**Why critical:** Essential for code exploration and learning

**Fix approach:**
1. Add logging to `hover.py` to see if called
2. Verify hover response format (MarkupContent structure)
3. Start with simple static hover (just show "NLPL Symbol")
4. Then add actual signature extraction
5. Test with functions, classes, variables

**Success criteria:**
- Hovering over function shows signature
- Hovering over class shows class definition
- Hovering over variable shows type (if available)

### Priority 3: Find References (Est: 1-2 hours)

**Why important:** Needed for code navigation and refactoring

**Fix approach:**
1. Add logging to `references.py`
2. Verify Location objects are formatted correctly
3. Test with simple single-file references first
4. Then test cross-file references
5. Verify includeDeclaration parameter works

**Success criteria:**
- Shift+F12 opens references panel
- Shows all usages of symbol
- Clicking reference navigates to location

---

## Testing Strategy Moving Forward

### Phase 1: Debug Broken Features (Days 3-4)

1. **Enable debug mode:**
   ```bash
   python -m nexuslang.lsp --stdio --debug --log-file /tmp/nlpl-lsp.log
   ```

2. **Add logging to each provider:**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"hover() called at {position}")
   ```

3. **Test one feature at a time**
4. **Commit fix after each working feature**

### Phase 2: Test Remaining Features (Day 5)

- Code Actions
- Signature Help
- Formatting
- Cross-file navigation

### Phase 3: Edge Cases & Polish (Days 6-7)

- Large file performance
- Invalid input handling
- Concurrent requests
- Workspace index accuracy

---

## Next Steps

1. **Tomorrow (Day 3):** Fix diagnostics provider
2. **Day 4:** Fix hover and references
3. **Day 5:** Test remaining features, write docs
4. **Days 6-7:** Performance testing and polish

**Target:** All 10 features working by end of Week 1 (Feb 23)
