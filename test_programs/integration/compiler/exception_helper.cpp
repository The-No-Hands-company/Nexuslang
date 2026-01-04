// C++ helper for testing NLPL exception handling
// This provides a function that throws, which NLPL can invoke

// NLPL exception structure - must match LLVM IR layout
// struct NLPLException { i8* message; }
struct NLPLException {
    const char* message;
    NLPLException(const char* msg) : message(msg) {}
};

// Extern "C" to avoid name mangling - callable from NLPL
extern "C" {

// Function that throws NLPL-compatible exception
void cpp_throw_error(const char* message) {
    throw NLPLException(message);
}

// Safe function that doesn't throw - for comparison
int cpp_safe_function(int a, int b) {
    return a + b;
}

}
