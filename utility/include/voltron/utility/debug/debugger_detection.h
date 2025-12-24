#pragma once

#include <string>
#include <iostream>

namespace voltron::utility::debug {

/// @brief Detect if running under a debugger
class DebuggerDetection {
public:
    /// Check if debugger is attached
    static bool isDebuggerPresent();

    /// Print debugger status
    static void printStatus(std::ostream& os = std::cout);
};

/// @brief Conditional breakpoint helper
#ifdef VOLTRON_ENABLE_DEBUG_BREAKS
    #if defined(__GNUC__) || defined(__clang__)
        #define VOLTRON_DEBUGBREAK() __builtin_trap()
    #elif defined(_MSC_VER)
        #define VOLTRON_DEBUGBREAK() __debugbreak()
    #else
        #define VOLTRON_DEBUGBREAK() std::abort()
    #endif

    #define VOLTRON_DEBUGBREAK_IF(cond) \
        do { if (cond) { VOLTRON_DEBUGBREAK(); } } while(0)
#else
    #define VOLTRON_DEBUGBREAK() ((void)0)
    #define VOLTRON_DEBUGBREAK_IF(cond) ((void)0)
#endif

} // namespace voltron::utility::debug
