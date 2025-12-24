#include "voltron/utility/assertions/assert_enhanced.h"
#include <cstdlib>
#include <mutex>

namespace voltron::utility::assertions {

namespace {
    std::mutex g_handler_mutex;
    AssertionHandler g_handler = nullptr;

    void defaultHandler(const char* expr, const char* msg, const std::source_location& loc, const std::stacktrace& trace) {
        std::cerr << "\n=== ASSERTION FAILED ===\n";
        std::cerr << "Expression: " << expr << "\n";
        std::cerr << "Message:    " << msg << "\n";
        std::cerr << "Location:   " << loc.file_name() << ":" << loc.line()
                  << " in " << loc.function_name() << "\n";
        
        std::cerr << "\nStack trace:\n" << trace << "\n";
        std::cerr << "========================\n\n";
        
        std::abort();
    }
}

void EnhancedAssert::assertFailed(const char* expression,
                                 const char* message,
                                 std::source_location location) {
    auto trace = std::stacktrace::current(1); // skip assertFailed frame
    
    std::unique_lock<std::mutex> lock(g_handler_mutex);
    if (g_handler) {
        g_handler(expression, message, location, trace);
    } else {
        defaultHandler(expression, message, location, trace);
    }
}

void EnhancedAssert::setHandler(AssertionHandler handler) {
    std::lock_guard<std::mutex> lock(g_handler_mutex);
    g_handler = std::move(handler);
}

void EnhancedAssert::resetHandler() {
    std::lock_guard<std::mutex> lock(g_handler_mutex);
    g_handler = nullptr;
}

} // namespace voltron::utility::assertions
