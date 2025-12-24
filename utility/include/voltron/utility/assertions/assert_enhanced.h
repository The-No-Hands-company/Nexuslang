#pragma once

#include <source_location>
#include <stacktrace>
#include <iostream>
#include <sstream>
#include <functional>
#include <string>

namespace voltron::utility::assertions {

/// @brief Callback type for assertion failures
using AssertionHandler = std::function<void(const char* expr, const char* msg, const std::source_location& loc, const std::stacktrace& trace)>;

/// @brief Enhanced assertion with stack trace, context, and custom handlers
class EnhancedAssert {
public:
    /// @brief Trigger an assertion failure
    static void assertFailed(const char* expression,
                            const char* message,
                            std::source_location location = std::source_location::current());

    /// @brief Set a custom assertion handler (e.g., for logging to disk or GUI)
    static void setHandler(AssertionHandler handler);

    /// @brief Reset to default handler (stderr + abort)
    static void resetHandler();
};

} // namespace voltron::utility::assertions

/// @brief Enhanced assertion macro with stack trace
/// Define VOLTRON_ENABLE_ASSERTS or VOLTRON_DEBUG to enable
#if defined(VOLTRON_ENABLE_ASSERTS) || defined(VOLTRON_DEBUG) || !defined(NDEBUG)
    #define VOLTRON_ASSERT(expr, msg) \
        do { \
            if (false == (static_cast<bool>(expr))) { \
                voltron::utility::assertions::EnhancedAssert::assertFailed(#expr, msg); \
            } \
        } while(0)
#else
    #define VOLTRON_ASSERT(expr, msg) ((void)0)
#endif

/// @brief Always-on assertion (even in release builds)
#define VOLTRON_VERIFY(expr, msg) \
    do { \
        if (false == (static_cast<bool>(expr))) { \
            voltron::utility::assertions::EnhancedAssert::assertFailed(#expr, msg); \
        } \
    } while(0)
