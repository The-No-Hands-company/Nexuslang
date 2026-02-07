# Generic Types Implementation - Bug Report

**Date**: February 7, 2026  
**Component**: LLVM IR Generator / Type System  
**Status**: Partial Fix Applied

## Issues Found

### 1. ✅ FIXED: Duplicate Type Declarations for Generic Specializations

**Severity**: Critical - Prevents compilation  
**Bug**: Generic specialized classes emitted twice in LLVM IR  
**Example**: `Box<Integer>` declared at both line 598 and 630 in output.ll

**Root Cause**:
- Main class type loop (line 294) iterated over ALL `self.class_types`
- Included specialized generics marked with `is_specialization: True`
- Same types appended to `late_type_declarations` (line 2066)
- Result: Two identical type declarations causing llc error

**Fix Applied** (Commit 37482da):
```python
# Line 297 in llvm_ir_generator.py
if class_info.get('is_specialization', False):
    continue
```

**Verification**:
- Before: `grep "^%Box_Integer = type" output.ll` showed 2 matches
- After: `grep "^%Box_Integer = type" output.ll` shows 1 match
- Generic classes compile successfully

---

### 2. ⚠️ OPEN: Generic Function Return Type Inference

**Severity**: High - Type safety violation  
**Bug**: Generic function specializations generate incorrect LLVM types  
**Example**: 

```nlpl
function identity<T> that takes value as T returns T
    return value
end

set str_result to identity with "Hello NLPL"  # Should be i8*, but generates i64
```

**LLVM IR Generated** (Incorrect):
```llvm
%24 = call i8* @identity_String(i8* %23)  ; Returns i8* (correct)
store i64 %24, i64* @str_result, align 8  ; Stores as i64 (WRONG!)
```

**Expected**:
```llvm
%24 = call i8* @identity_String(i8* %23)
store i8* %24, i8** @str_result, align 8  ; Should be i8** not i64*
```

**Root Cause**:
Variable type inference doesn't resolve generic function return types.
When `set str_result to identity with "Hello NLPL"` is parsed:
1. Parser doesn't know `identity` is generic function
2. Type system defaults to `Integer` (i64) for untyped variables
3. Generic specialization creates correct `identity_String` returning i8*
4. But variable `str_result` already typed as i64
5. Type mismatch causes llc error

**Location**: Likely in `src/nlpl/compiler/backends/llvm_ir_generator.py`
- Variable declaration handling (~line 800-900)
- Generic function call type resolution (~line 2100-2200)
- Type inference system integration

**Workaround**: Use explicit typing or avoid generic functions with different return types

**Proper Fix Required**:
1. Type inference must track generic function signatures
2. When assigning result of generic function call, infer return type
3. Store resolved type parameters during specialization
4. Apply type substitutions to variable declarations

---

### 3. ⚠️ OPEN: Memory Initialization for Generic Class Properties

**Severity**: Medium - Correctness issue  
**Bug**: Generic class properties show as 0 after explicit assignment  

**Example**:
```nlpl
set int_box to new Box<Integer>
set int_box.value to 42      # Assigns 42
print text call int_box.get_value  # Prints 0 (WRONG!)
```

**Expected**: Should print 42  
**Actual**: Prints 0

**Likely Cause**:
- Stack allocation for generic class instances
- Properties not properly initialized in constructor
- Assignment might use wrong offset or not persist

**Investigation Needed**:
- Check LLVM IR for `alloca %Box_Integer`
- Verify `getelementptr` offsets for property access
- Ensure `store` instructions write to correct addresses
- Check if object is heap vs stack allocated

---

## Impact Assessment

| Issue | Impact | Fixed | Priority |
|-------|--------|-------|----------|
| Duplicate type declarations | Compilation blocked | ✅ Yes | Critical |
| Generic function type inference | Type safety broken | ❌ No | High |
| Memory initialization | Wrong values | ❌ No | Medium |

## Next Steps

1. **Immediate**: Generic function type inference fix
   - Implement proper return type tracking
   - Update variable type resolution
   - Test with multiple generic function calls

2. **Short-term**: Memory initialization investigation
   - Generate debug LLVM IR
   - Trace property assignment flow
   - Fix constructor/initializer generation

3. **Long-term**: Comprehensive generic types testing
   - Test suite for all generic patterns
   - Edge cases (nested generics, constraints, etc.)
   - Performance benchmarking

## Workarounds for Users

**Until generic function type inference is fixed:**
```nlpl
# ❌ Avoid this pattern:
set result to generic_func with some_value

# ✅ Use this instead:
# Explicitly type variables or use classes only
class Holder<T>
    property value as T
end class
```

**Generic classes work correctly** (except memory init):
- Use `Box<T>`, `Pair<K,V>`, `Optional<T>` patterns
- Methods with generic parameters work
- Type safety maintained at compile time

## References

- Commit 37482da: Fix duplicate type declarations
- Commit 4a910f9: Add working generic classes example
- `examples/18_generic_classes_working.nlpl`: Reference implementation
- ROADMAP.md: 37/37 generic tests passing (pre-LLVM backend)
