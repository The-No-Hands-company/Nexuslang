# LLVM Native Compilation Status

## Summary
Successfully fixed critical bugs in LLVM backend. **5 out of 7** test examples now compile to native executables.

## Fixed Bugs (Session 2 - Jan 22, 2025)

### Bug 1: Type Promotion in Binary Operations ✅
**Problem**: Type inference returned left operand type instead of promoted type
```nlpl
set total to quantity times unit_price  # quantity=i64, unit_price=double
# Expected: result type = double (promoted)
# Actual: result type = i64 (left operand)
```
**Root Cause**: `_infer_expression_type()` returned `left_type` for BinaryOperation
**Solution**: Changed to `return self._promote_types(left_type, right_type)`
**File**: `src/nlpl/compiler/backends/llvm_ir_generator.py` lines 8630-8651

### Bug 2: sprintf Declaration Placement ✅  
**Problem**: sprintf declared inside function body instead of header
```llvm
define i64 @some_function() {
  declare i32 @sprintf(i8*, i8*, ...)  # ERROR: declarations must be at module level
}
```
**Root Cause**: Inline emit during type cast generation
**Solution**:
1. Added sprintf to header generation (line 451-452)
2. Removed inline declaration, register in extern_functions (line 4930-4933)
**File**: `src/nlpl/compiler/backends/llvm_ir_generator.py`

### Bug 3: TypeCastExpression Type Inference ✅
**Problem**: TypeCastExpression always inferred as i64, breaking string concat
```nlpl
return "$" plus convert amount to string
# "$" = i8* (correct)
# convert amount to string = i64 (WRONG, should be i8*)
# String concat not triggered because right_type != i8*
```
**Root Cause**: `_infer_expression_type()` had no case for TypeCastExpression, fell through to default i64
**Solution**: Added TypeCastExpression handler returning correct types based on target_type
```python
elif expr_type == 'TypeCastExpression':
    target_type = expr.target_type.lower()
    if target_type == 'string':
        return 'i8*'
    elif target_type in ('integer', 'int'):
        return 'i64'
    # ... other types
```
**File**: `src/nlpl/compiler/backends/llvm_ir_generator.py` lines 8835-8847

### Bug 4: sprintf Temp Register Assignment ✅
**Problem**: sprintf call didn't assign result to temp register
```llvm
%4 = alloca i8, i32 32
call i32 (...) @sprintf(i8* %4, ...)  # Missing %5 = 
%6 = call i64 @strlen(i8* %1)        # ERROR: expected %5 not %6
```
**Root Cause**: sprintf returns i32 but we weren't capturing it
**Solution**: Added temp register assignment for sprintf result
```python
sprintf_result = self._new_temp()
self.emit(f'{indent}{sprintf_result} = call i32 (i8*, i8*, ...) @sprintf(...)')
```
**File**: `src/nlpl/compiler/backends/llvm_ir_generator.py` lines 4940, 4947

## Compilation Status

### ✅ Working Examples (5/7)
| Example | Description | Status |
|---------|-------------|--------|
| 01_basic_concepts.nlpl | Variables, functions, control flow | ✅ Compiles & runs |
| 04_type_system_basics.nlpl | Type inference, conversions | ✅ Compiles & runs |
| 08_advanced_type_features_index.nlpl | Type aliases, guards | ✅ Compiles & runs |
| 11_traits.nlpl | Trait system | ✅ Compiles & runs |
| 25_ffi_c_interop.nlpl | C library bindings | ✅ Compiles & runs |

### ❌ Failing Examples (2/7)
| Example | Error | Root Cause |
|---------|-------|------------|
| 26_ffi_struct_marshalling.nlpl | double vs i64 type mismatch | Unknown - needs investigation |
| 32_feature_showcase.nlpl | i64 passed as i8* to printf | print text expects string, got integer |

## Known Issues

### 1. String Formatting - NULL Terminator Display
**Symptom**: Output shows "\00" characters
```
Unit Price: $19.990000\00
```
**Cause**: String constants include explicit null terminator in format
**Severity**: Low (cosmetic)
**Fix**: Remove "\00" suffix from generated strings

### 2. Print Integer Without Conversion
**Symptom**: `print text <integer>` fails with type error
```nlpl
set x to 42
print text x  # ERROR: i64 passed as i8* to printf
```
**Cause**: print text expects string, no auto-conversion
**Severity**: Medium (usability)
**Fix**: Add implicit conversion or use separate `print number` statement

## Next Steps

1. Fix example 26 type error (double vs i64 mismatch)
2. Fix example 32 integer printing issue
3. Add implicit int-to-string conversion for print statements
4. Fix string formatting to remove visible null terminators
5. Performance benchmarks (native vs interpreted)

## Compiler Usage

```bash
# Compile only
./nlplc examples/01_basic_concepts.nlpl -o output

# Compile and run
./nlplc examples/01_basic_concepts.nlpl -o output --run

# View LLVM IR
./nlplc examples/01_basic_concepts.nlpl --emit-llvm

# Optimize (O2)
./nlplc examples/01_basic_concepts.nlpl -o output --optimize 2

# Verbose mode
./nlplc examples/01_basic_concepts.nlpl -o output --verbose
```

## Technical Details

**Compilation Pipeline**:
```
.nlpl → Lexer → Parser → AST → LLVM IR → Object File → Executable
                                  ↓
                            test_program.ll (human-readable)
                                  ↓
                            test_program.o (machine code)
                                  ↓
                            test_program (linked executable)
```

**LLVM IR Generator**:
- Lines changed: ~30 across 4 bug fixes
- Total file size: 9769 lines
- Key methods:
  - `_generate_binary_operation()` - Arithmetic, logic, comparisons
  - `_generate_type_cast_expression()` - Type conversions
  - `_infer_expression_type()` - Static type analysis
  - `_generate_string_concat()` - String concatenation helper

**Linking**:
- `-lm` - Math library (sin, cos, sqrt, etc.)
- `-lpthread` - POSIX threads
- `-lstdc++` - C++ standard library (exception handling)

## Session Timeline

**Jan 21, 2025**:
- Created nlplc compiler tool
- Fixed name collision bug (add_sep variable vs label)
- Fixed float default return values
- First successful native compilation (example 01)

**Jan 22, 2025**:
- Fixed type promotion bug in binary operations
- Fixed sprintf declaration placement
- Fixed TypeCastExpression type inference
- Fixed sprintf temp register assignment
- **Achievement**: 5/7 examples compiling natively

## Success Metrics

- **Examples compiling**: 5/7 (71%)
- **Bugs fixed**: 4 critical type system bugs
- **Lines changed**: ~30 lines
- **Native execution**: All 5 compiled examples run successfully
- **Performance**: Native code vs interpreted (benchmarks pending)

