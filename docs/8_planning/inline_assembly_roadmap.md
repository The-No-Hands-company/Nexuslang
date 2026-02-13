# Inline Assembly Completion - Implementation Roadmap

**Feature:** Complete Inline Assembly Support  
**Priority:** HIGH (Quick Win - Phase 1)  
**Estimated Effort:** 1-2 months  
**Status:** ⚠️ PARTIAL (Parser complete, LLVM backend needed)  
**Start Date:** February 13, 2026

---

## Executive Summary

Inline assembly is **partially implemented** in NLPL with full parser support but requires LLVM backend completion for compiled mode execution. This feature is critical for:

- Direct hardware control (complement to Port I/O, MMIO, DMA, CPU Control)
- Performance-critical code sections
- Architecture-specific optimizations
- Bootloader and OS kernel development
- Device driver implementation

**Key Achievement Target:** 100% completion of Part 2 (Low-Level Primitives), giving NLPL **complete parity** with C/C++/Rust/ASM for systems programming.

---

## Current Implementation Status

### ✅ COMPLETE Components

**1. Lexer Tokens (src/nlpl/parser/lexer.py)**
- `ASM` - Short form keyword
- `INLINE` - Long form keyword
- Both recognized in keyword map

**2. Parser Support (src/nlpl/parser/parser.py)**
- `parse_inline_assembly()` - Lines 3415-3510
- Full syntax parsing:
  ```nlpl
  asm
      code
          "mov rax, rbx"
          "add rax, 5"
      inputs "r": x, "r": y
      outputs "=r": result
      clobbers "rax", "rbx"
  end
  ```
- Section parsing:
  - `code` - Assembly instructions (string literals)
  - `inputs` - Input operands with constraints
  - `outputs` - Output operands with constraints
  - `clobbers` - Clobbered registers
- Helper methods:
  - `_parse_asm_operands()` - Parse input/output operands
  - `_parse_asm_clobbers()` - Parse clobbered registers

**3. AST Node (src/nlpl/parser/ast.py)**
- `InlineAssembly` class
- Fields:
  - `asm_code` - List of assembly instructions
  - `inputs` - Dict mapping constraints to expressions
  - `outputs` - Dict mapping constraints to variables
  - `clobbers` - List of register names
  - `line_number` - Source location

**4. Interpreter Placeholder (src/nlpl/interpreter/interpreter.py)**
- `execute_inline_assembly()` - Lines 885-895
- Currently returns None with comment explaining compiled-mode requirement
- Proper structure for future LLVM implementation

### ❌ MISSING Components

**1. LLVM IR Generation**
- No `codegen_inline_assembly()` in compiler backend
- Need to generate LLVM inline assembly instructions
- Must handle constraint translation (NLPL → LLVM)

**2. Register Constraints**
- No constraint validation
- No constraint translation (e.g., "r" → any register, "a" → rax)
- No architecture-specific constraint handling

**3. Multi-Architecture Support**
- No x86/x64 specific handling
- No ARM support
- No architecture detection/selection

**4. Safety Features**
- No validation of assembly syntax
- No register conflict detection
- No dangerous instruction warnings

**5. Testing & Documentation**
- No test files for inline assembly
- No example programs demonstrating usage
- No comprehensive documentation

---

## Implementation Plan

### **Week 1-2: LLVM Backend Foundation**

**Goals:**
- Implement basic LLVM inline assembly generation
- Support simple single-instruction blocks
- x86/x64 architecture support

**Tasks:**
1. Create `codegen_inline_assembly()` in LLVM compiler backend
2. Implement constraint translation (NLPL → LLVM syntax)
3. Generate LLVM inline assembly calls
4. Handle basic input/output operands
5. Test with simple examples (mov, add, nop)

**Deliverables:**
- Basic inline assembly working in compiled mode
- Simple test cases passing

---

### **Week 3-4: Register Constraints**

**Goals:**
- Complete constraint system
- Support all x86/x64 constraint types
- Proper register allocation interface

**Tasks:**
1. Implement constraint validation
2. Support constraint types:
   - `"r"` - Any general register
   - `"a"` - RAX/EAX/AX/AL
   - `"b"` - RBX/EBX/BX/BL
   - `"c"` - RCX/ECX/CX/CL
   - `"d"` - RDX/EDX/DX/DL
   - `"S"` - RSI/ESI/SI
   - `"D"` - RDI/EDI/DI
   - `"m"` - Memory operand
   - `"i"` - Immediate integer
   - `"n"` - Known constant
   - `"g"` - General (register, memory, or immediate)
3. Implement output constraints:
   - `"=r"` - Write-only register
   - `"+r"` - Read-write register
   - `"=m"` - Write-only memory
4. Handle constraint modifiers:
   - `&` - Early clobber
   - `%` - Commutative
5. Register conflict detection

**Deliverables:**
- Complete constraint system
- Validation and error checking
- Comprehensive constraint tests

---

### **Week 5-6: Multi-Instruction Blocks & Clobbers**

**Goals:**
- Support complex multi-instruction sequences
- Proper clobber list handling
- Instruction scheduling awareness

**Tasks:**
1. Multi-instruction block generation
2. Clobber list processing:
   - Register clobbers ("rax", "rbx", etc.)
   - Special clobbers ("memory", "cc", "flags")
3. Instruction ordering preservation
4. Label support within inline assembly
5. Jump target handling

**Deliverables:**
- Complex inline assembly blocks working
- Proper register preservation
- Clobber tests passing

---

### **Week 7: Architecture Support**

**Goals:**
- Detect target architecture
- Support multiple architectures
- Architecture-specific constraints

**Tasks:**
1. Architecture detection (x86/x64/ARM/AArch64)
2. x86-specific features:
   - 32-bit and 64-bit modes
   - Register name translation
   - Instruction set extensions (SSE, AVX)
3. ARM/AArch64 constraints (future)
4. Architecture-specific validation

**Deliverables:**
- Architecture detection working
- x86/x64 fully supported
- Foundation for ARM support

---

### **Week 8: Safety & Validation**

**Goals:**
- Syntax validation
- Dangerous instruction warnings
- Best practices enforcement

**Tasks:**
1. Basic assembly syntax validation
2. Dangerous instruction detection:
   - Stack manipulation warnings
   - Privileged instructions
   - Self-modifying code warnings
3. Register usage analysis
4. Memory access validation
5. Helpful error messages

**Deliverables:**
- Syntax validation working
- Safety warnings implemented
- Error messages clear and helpful

---

## Testing Strategy

### **Unit Tests (test_programs/unit/assembly/)**

1. **test_asm_basic.nlpl**
   - Simple single instructions (nop, mov)
   - Input operands
   - Output operands
   - Basic constraints

2. **test_asm_constraints.nlpl**
   - All constraint types
   - Constraint validation
   - Error cases

3. **test_asm_multi_instruction.nlpl**
   - Multi-instruction blocks
   - Label usage
   - Jump targets

4. **test_asm_clobbers.nlpl**
   - Register clobbers
   - Memory clobbers
   - Condition code clobbers

5. **test_asm_errors.nlpl**
   - Invalid syntax
   - Constraint violations
   - Register conflicts

### **Integration Tests (test_programs/integration/assembly/)**

1. **test_asm_with_hardware.nlpl**
   - Combine with Port I/O
   - Combine with MMIO
   - Combine with CPU Control

2. **test_asm_performance.nlpl**
   - Fast math operations
   - SIMD operations
   - Performance-critical loops

3. **test_asm_os_kernel.nlpl**
   - Task switching
   - Interrupt handlers
   - System call entry/exit

### **Example Programs (examples/)**

1. **examples/inline_assembly_guide.nlpl** (500+ lines)
   - Complete guide to inline assembly
   - All constraint types demonstrated
   - Real-world use cases
   - Best practices

2. **examples/hardware_inline_asm.nlpl**
   - Hardware control examples
   - Direct register access
   - Performance optimizations

---

## Syntax Reference

### Basic Syntax

```nlpl
# Simple inline assembly
asm
    code
        "nop"
        "mov rax, 0"
end

# With inputs
set x to 10
set y to 20
asm
    code
        "mov rax, %0"
        "add rax, %1"
    inputs "r": x, "r": y
end

# With outputs
set result to 0
asm
    code
        "mov rax, 42"
    outputs "=r": result
end

# Complete example
function fast_multiply with a as Integer and b as Integer returns Integer
    set result to 0
    
    asm
        code
            "mov rax, %1"
            "imul rax, %2"
        inputs "r": a, "r": b
        outputs "=r": result
        clobbers "rax"
    end
    
    return result
end
```

### Constraint Types

```nlpl
# Register constraints
"r"   # Any general register
"a"   # RAX register
"b"   # RBX register
"c"   # RCX register
"d"   # RDX register

# Memory constraints
"m"   # Memory operand
"=m"  # Output to memory

# Immediate constraints
"i"   # Immediate integer
"n"   # Known constant
"g"   # General (register, memory, or immediate)

# Output constraints
"=r"  # Write-only register
"+r"  # Read-write register

# Modifiers
"=&r" # Early clobber
```

### Architecture-Specific Features

```nlpl
# x86-64 specific
asm
    code
        "rdtsc"              # Read timestamp counter
        "shl rdx, 32"        # Shift high bits
        "or rax, rdx"        # Combine result
    outputs "=a": low, "=d": high
    clobbers "cc"
end

# SIMD operations
asm
    code
        "movaps xmm0, %0"    # Load 4 floats
        "mulps xmm0, %1"     # Multiply
        "movaps %2, xmm0"    # Store result
    inputs "m": input1, "m": input2
    outputs "=m": result
    clobbers "xmm0"
end
```

---

## Use Cases

### 1. Performance-Critical Code

```nlpl
# Fast bit counting (population count)
function count_bits with value as Integer returns Integer
    set result to 0
    
    asm
        code
            "popcnt rax, %1"
        inputs "r": value
        outputs "=r": result
    end
    
    return result
end
```

### 2. Hardware Control

```nlpl
# Read timestamp counter (cycles since boot)
function read_tsc returns Integer
    set low to 0
    set high to 0
    
    asm
        code
            "rdtsc"
        outputs "=a": low, "=d": high
    end
    
    # Combine 32-bit halves into 64-bit result
    return (high shift left 32) bitwise or low
end
```

### 3. OS Kernel Development

```nlpl
# Switch to user mode
function switch_to_user_mode with user_stack as Integer
    asm
        code
            "mov rsp, %0"     # Load user stack
            "push 0x23"       # User data selector
            "push %0"         # User stack
            "push 0x202"      # EFLAGS (interrupts enabled)
            "push 0x1B"       # User code selector
            "push user_entry" # User entry point
            "iretq"           # Return to user mode
        inputs "r": user_stack
        clobbers "rsp", "memory"
    end
end
```

### 4. SIMD Optimizations

```nlpl
# Vectorized addition (4 floats at once)
function vec4_add with a as Array of Float and b as Array of Float returns Array of Float
    set result to create empty array
    
    asm
        code
            "movups xmm0, [%0]"  # Load 4 floats from a
            "movups xmm1, [%1]"  # Load 4 floats from b
            "addps xmm0, xmm1"   # Add vectors
            "movups [%2], xmm0"  # Store result
        inputs "r": a, "r": b
        outputs "=r": result
        clobbers "xmm0", "xmm1"
    end
    
    return result
end
```

---

## Integration with NLPL Ecosystem

### With Hardware Access

```nlpl
# Combine inline assembly with Port I/O
function fast_port_read with port as Integer returns Integer
    set value to 0
    
    asm
        code
            "mov dx, %1"      # Port number in DX
            "in al, dx"       # Read byte from port
        inputs "r": port
        outputs "=a": value
    end
    
    return value
end
```

### With Memory Management

```nlpl
# Fast memory copy using REP MOVSB
function fast_memcpy with dest as Pointer and src as Pointer and count as Integer
    asm
        code
            "mov rdi, %0"     # Destination
            "mov rsi, %1"     # Source
            "mov rcx, %2"     # Count
            "rep movsb"       # Copy bytes
        inputs "r": dest, "r": src, "r": count
        clobbers "rdi", "rsi", "rcx", "memory"
    end
end
```

---

## Completion Criteria

### ✅ Feature Complete When:

1. **LLVM Backend Working**
   - Generates correct inline assembly IR
   - Handles all constraint types
   - Proper register allocation

2. **Constraints Validated**
   - All constraint types supported
   - Proper error messages
   - Register conflict detection

3. **Multi-Instruction Support**
   - Complex blocks working
   - Labels and jumps supported
   - Clobber lists handled

4. **Architecture Support**
   - x86/x64 fully supported
   - Architecture detection working
   - Foundation for ARM

5. **Safety Features**
   - Syntax validation
   - Dangerous instruction warnings
   - Clear error messages

6. **Testing Complete**
   - 5+ unit test files
   - 3+ integration tests
   - 2+ example programs
   - All tests passing

7. **Documentation Complete**
   - Comprehensive guide
   - Constraint reference
   - Use case examples
   - Best practices

---

## Dependencies

### Required Knowledge

- LLVM inline assembly syntax
- x86/x64 assembly language
- Register allocation concepts
- Calling conventions
- ABI compatibility

### External Dependencies

- LLVM compiler infrastructure
- Target architecture support
- Assembly syntax knowledge

### Internal Dependencies

- LLVM compiler backend (codegen module)
- AST nodes (InlineAssembly)
- Type system (for operand validation)

---

## Risk Assessment

### LOW RISK
- Parser already complete
- AST structure defined
- Clear implementation path

### MEDIUM RISK
- LLVM inline assembly API complexity
- Constraint validation edge cases
- Architecture-specific behavior

### HIGH RISK
- None identified (well-understood problem domain)

---

## Success Metrics

### Performance Targets
- Zero overhead vs. native C inline assembly
- Proper register allocation
- Optimal instruction scheduling

### Compatibility Targets
- GCC inline assembly syntax compatible
- Clang inline assembly syntax compatible
- LLVM IR inline assembly compatible

### Quality Targets
- 100% test coverage
- Comprehensive documentation
- Clear error messages

---

## Timeline Summary

| Week | Milestone | Deliverable |
|------|-----------|-------------|
| 1-2 | LLVM Backend Foundation | Basic inline assembly working |
| 3-4 | Register Constraints | Complete constraint system |
| 5-6 | Multi-Instruction Support | Complex blocks working |
| 7 | Architecture Support | x86/x64 fully supported |
| 8 | Safety & Validation | Production-ready |

**Total Duration:** 8 weeks (2 months)  
**End Date:** ~April 13, 2026

---

## Next Steps (Immediate Actions)

1. **Review LLVM inline assembly documentation**
2. **Create basic LLVM IR generation stub**
3. **Implement simple constraint translation**
4. **Write first test case (nop instruction)**
5. **Verify compilation pipeline integration**

---

## Post-Completion Impact

**After inline assembly completion:**

- ✅ Part 2 (Low-Level Primitives) = **100% COMPLETE**
- ✅ NLPL has **complete parity** with C/C++/Rust for systems programming
- ✅ Full hardware control capability
- ✅ Performance optimization toolkit complete
- ✅ OS kernel development fully enabled
- ✅ Device driver development fully supported

**This positions NLPL as a truly universal systems programming language, ready for Phase 2 (Universal Infrastructure) implementation.**

---

**Document Created:** February 13, 2026  
**Last Updated:** February 13, 2026  
**Status:** READY FOR IMPLEMENTATION
