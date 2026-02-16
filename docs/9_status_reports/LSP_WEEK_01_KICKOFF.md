# LSP Week 1 Kickoff - Cross-File Navigation

**Week:** February 15-21, 2026  
**Status:** 🟢 STARTING  
**Focus:** Workspace-wide symbol indexing and cross-file navigation

---

## Week 1 Goals

By **February 21, 2026**, complete:

1. ✅ Workspace-wide symbol indexing (parse all .nlpl files on startup)
2. ✅ Enhanced go-to-definition across files (jump to imported symbols)
3. ✅ Document outline (tree view of functions/classes)
4. ✅ Call hierarchy support (find callers/callees)

**Success Metric:** Cross-file navigation working in multi-file test project (5+ files)

---

## Day 1 (Today - Feb 15): Setup & Symbol Indexing Design

### Morning Tasks (2-3 hours)
- [x] Read LSP completion roadmap
- [ ] Review existing LSP codebase structure
  - Read `src/nlpl/lsp/server.py` (understand server architecture)
  - Read `src/nlpl/lsp/definitions.py` (understand current go-to-def)
  - Read `src/nlpl/lsp/symbols.py` (understand workspace symbols)
- [ ] Design workspace symbol indexing system
  - Decide on data structure (global symbol table: `Dict[str, List[SymbolInfo]]`)
  - Decide on indexing strategy (startup vs lazy vs incremental)
  - Sketch out SymbolInfo dataclass (name, kind, location, scope)

### Afternoon Tasks (3-4 hours)
- [ ] Implement basic workspace scanner
  - Create `src/nlpl/lsp/workspace_index.py`
  - Implement `WorkspaceIndex` class
  - Add `scan_workspace()` method (find all .nlpl files recursively)
  - Add `index_file()` method (parse file, extract symbols)
  - Add `get_symbol()` method (lookup symbol by name)

**Code Skeleton:**
```python
# src/nlpl/lsp/workspace_index.py
"""Workspace-wide symbol indexing for cross-file navigation."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import os

@dataclass
class SymbolInfo:
    """Information about a symbol in the workspace."""
    name: str
    kind: str  # 'function', 'class', 'variable', 'struct', 'method'
    file_uri: str
    line: int
    column: int
    scope: Optional[str] = None  # Module or class scope
    signature: Optional[str] = None  # For functions/methods
    
class WorkspaceIndex:
    """Indexes all symbols in the workspace for fast lookup."""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.symbols: Dict[str, List[SymbolInfo]] = {}  # name -> list of symbols
        self.files: Dict[str, List[SymbolInfo]] = {}  # file_uri -> symbols in file
        
    def scan_workspace(self) -> None:
        """Scan workspace for all .nlpl files and index symbols."""
        # TODO: Recursively find all .nlpl files
        # TODO: Call index_file() for each
        pass
        
    def index_file(self, file_path: str) -> List[SymbolInfo]:
        """Parse a single file and extract all symbols."""
        # TODO: Parse file to AST
        # TODO: Walk AST, extract symbols
        # TODO: Store in self.symbols and self.files
        pass
        
    def get_symbol(self, name: str) -> List[SymbolInfo]:
        """Get all symbols with given name."""
        return self.symbols.get(name, [])
        
    def get_symbols_in_file(self, file_uri: str) -> List[SymbolInfo]:
        """Get all symbols defined in a file."""
        return self.files.get(file_uri, [])
```

**Deliverable:** `workspace_index.py` skeleton with basic structure

---

## Day 2 (Feb 16): Implement Symbol Extraction from AST

### Tasks (6-7 hours)
- [ ] Implement AST walking for symbol extraction
  - Handle `FunctionDefinition` nodes (extract function name, params, return type)
  - Handle `ClassDefinition` nodes (extract class name, methods)
  - Handle `StructDefinition` nodes (extract struct name, fields)
  - Handle `VariableDeclaration` nodes (extract top-level variables)
  - Handle method definitions inside classes

- [ ] Add symbol kind detection
  - Distinguish between functions, classes, methods, variables
  - Track scope (module-level vs class-level)

- [ ] Test symbol extraction
  - Create `tests/test_workspace_index.py`
  - Test with simple NLPL file (1 function, 1 class)
  - Verify symbols extracted correctly

**Example Test:**
```python
# tests/test_workspace_index.py
def test_extract_function_symbols():
    code = """
    function greet with name as String returns String
        return "Hello " + name
    end
    """
    # Parse to AST
    # Extract symbols
    # Assert: 1 function symbol named 'greet'
```

**Deliverable:** Symbol extraction working for functions and classes

---

## Day 3 (Feb 17): Workspace Scanning & Indexing

### Tasks (6-7 hours)
- [ ] Implement `scan_workspace()`
  - Use `os.walk()` to find all .nlpl files
  - Skip hidden directories (.git, __pycache__)
  - Handle symlinks gracefully
  - Report progress (optional: send to LSP client)

- [ ] Implement incremental re-indexing
  - Detect when a file changes (LSP textDocument/didChange)
  - Re-index only that file
  - Update global symbol table
  - Invalidate old symbols from that file

- [ ] Optimize indexing performance
  - Use multiprocessing for parallel file parsing
  - Measure indexing time (target: <1s for 100 files)
  - Add caching (pickle symbol table to disk)

- [ ] Integrate with LSP server
  - Call `workspace_index.scan_workspace()` on server initialize
  - Hook into textDocument/didChange for incremental updates

**Deliverable:** Workspace indexing working, tested with 50+ file project

---

## Day 4 (Feb 18): Cross-File Go-to-Definition

### Tasks (6-7 hours)
- [ ] Enhance `definitions.py` for cross-file support
  - When symbol not found in current file, check `WorkspaceIndex`
  - Handle imports (resolve imported symbols to their definition files)
  - Return `Location` with correct file URI

- [ ] Implement import resolution
  - Parse import statements (AST: `ImportStatement`)
  - Map imported names to file paths
  - Handle `import module` vs `from module import symbol`

- [ ] Test cross-file navigation
  - Create test project:
    - `math_utils.nlpl`: defines `add(a, b)` function
    - `main.nlpl`: imports and calls `add()`
  - Verify go-to-definition on `add()` call jumps to `math_utils.nlpl`

**Example Test Project:**
```nlpl
# test_project/math_utils.nlpl
function add with a as Integer and b as Integer returns Integer
    return a + b
end

# test_project/main.nlpl
import math_utils

set result to math_utils.add with a: 5 and b: 3
print text result  # Ctrl+Click on 'add' should jump to math_utils.nlpl
```

**Deliverable:** Cross-file go-to-definition working

---

## Day 5 (Feb 19): Document Outline & Call Hierarchy

### Morning: Document Outline (3-4 hours)
- [ ] Implement document outline provider
  - Add `textDocument/documentSymbol` handler to LSP server
  - Return hierarchical symbol tree (functions, classes, methods)
  - Include symbol kind, name, range, selection range

- [ ] Test in VS Code
  - Open NLPL file in VS Code
  - Verify outline view shows functions/classes
  - Verify clicking outline item navigates to symbol

**LSP Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": [
    {
      "name": "MyClass",
      "kind": 5,  // Class
      "range": { "start": { "line": 10, "character": 0 }, "end": { "line": 20, "character": 0 } },
      "children": [
        {
          "name": "my_method",
          "kind": 6,  // Method
          "range": { ... }
        }
      ]
    }
  ]
}
```

### Afternoon: Call Hierarchy (3-4 hours)
- [ ] Implement call hierarchy provider
  - Add `textDocument/prepareCallHierarchy` handler
  - Add `callHierarchy/incomingCalls` handler (find callers)
  - Add `callHierarchy/outgoingCalls` handler (find callees)

- [ ] Build call graph
  - Walk AST to find all function calls
  - Map function calls to their definitions
  - Support recursive navigation (caller of caller)

- [ ] Test call hierarchy
  - Create test with function call chain: `main() -> process() -> validate()`
  - Verify "Find Callers" on `validate()` shows `process()`
  - Verify "Find Callees" on `process()` shows `validate()`

**Deliverable:** Document outline and call hierarchy working

---

## Day 6 (Feb 20): Testing & Bug Fixes

### Tasks (6-7 hours)
- [ ] Comprehensive testing
  - Test with large workspace (100+ files)
  - Test with deeply nested imports (A imports B imports C)
  - Test with circular imports (graceful handling)
  - Test with invalid files (don't crash indexer)

- [ ] Performance validation
  - Measure indexing time for 100-file workspace (target: <1s)
  - Profile slow parts (cProfile)
  - Optimize if needed

- [ ] Bug fixes
  - Fix any crashes found during testing
  - Handle edge cases (empty files, parse errors, missing imports)

- [ ] Documentation
  - Document workspace indexing design in `src/nlpl/lsp/README.md`
  - Add comments to complex code sections

**Test Scenarios:**
1. Empty workspace (0 files) - no crash
2. Single file workspace - indexing works
3. 100-file workspace - indexing <1s
4. File with parse errors - skip gracefully
5. Circular imports - detect and handle
6. Rename imported symbol - update all references

**Deliverable:** Robust, tested workspace indexing

---

## Day 7 (Feb 21): Integration & Week Wrap-up

### Morning: Integration Testing (3-4 hours)
- [ ] Test in real VS Code workflow
  - Open multi-file NLPL project
  - Edit files, verify incremental indexing works
  - Test go-to-definition across files
  - Test document outline
  - Test call hierarchy

- [ ] Test with existing NLPL examples
  - Use `examples/` directory as test workspace
  - Verify navigation works on real NLPL code

### Afternoon: Documentation & Reporting (2-3 hours)
- [ ] Write week 1 status report
  - Document completed features
  - List known issues / limitations
  - Measure performance metrics
  - Plan for next week

- [ ] Update LSP README
  - Add "Cross-File Navigation" section
  - Document workspace indexing architecture
  - Add usage examples

- [ ] Commit and push
  - Clean up code, remove debug prints
  - Write clear commit messages
  - Push to GitHub

**Deliverable:** Week 1 complete, status report published

---

## Success Criteria (End of Week 1)

Must Have:
- ✅ Workspace indexing scans all .nlpl files on startup
- ✅ Global symbol table built (functions, classes, structs)
- ✅ Go-to-definition works across files
- ✅ Document outline shows file structure in VS Code
- ✅ Call hierarchy finds callers and callees
- ✅ Performance: <1s indexing for 100 files
- ✅ Tests passing for all new features

Nice to Have:
- 🎯 Parallel file parsing (multiprocessing)
- 🎯 Persistent cache (save symbol table to disk)
- 🎯 Progress reporting to client ("Indexing 45/100 files")

Blockers to Escalate:
- ❌ AST parsing too slow (>5s for 100 files)
- ❌ Import resolution doesn't work
- ❌ Crashes on large workspaces

---

## Resources

**Code to Read:**
- `src/nlpl/lsp/server.py` - LSP server main loop
- `src/nlpl/lsp/definitions.py` - Current go-to-definition implementation
- `src/nlpl/lsp/symbols.py` - Workspace symbol search
- `src/nlpl/parser/parser.py` - AST node definitions
- `src/nlpl/modules/module_loader.py` - Import resolution

**Documentation:**
- LSP Spec: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/
- textDocument/documentSymbol: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol
- Call Hierarchy: https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_prepareCallHierarchy

**Tools:**
- cProfile for performance profiling
- pytest for testing
- VS Code for manual testing

---

## Daily Standup Questions

Each day, answer:
1. **What did I complete yesterday?**
2. **What will I work on today?**
3. **Any blockers or challenges?**

Log answers in this document or a separate daily log.

---

## Let's Go! 🚀

Start with Day 1 tasks. Focus on getting the basic infrastructure in place before optimizing. Remember: **working code first, fast code second**.

Good luck! You've got this. 💪
