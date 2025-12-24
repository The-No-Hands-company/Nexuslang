#pragma once

/// @file voltron_utility.h
/// @brief Master include header for Voltron 3D utility toolkit
/// Include this single header to access all utility categories

// Memory Debugging
#include "voltron/utility/memory/memory_tracker.h"
#include "voltron/utility/memory/smart_ptr_debug.h"
#include "voltron/utility/memory/allocation_guard.h"
#include "voltron/utility/memory/buffer_overflow_detector.h"
#include "voltron/utility/memory/double_free_detector.h"

// Crash Handling
#include "voltron/utility/crash/stacktrace_capture.h"
#include "voltron/utility/crash/signal_handler.h"

// Logging
#include "voltron/utility/logging/logger.h"
#include "voltron/utility/logging/log_macros.h"

// Profiling
#include "voltron/utility/profiling/scoped_timer.h"

// Assertions & Contracts
#include "voltron/utility/assertions/assert_enhanced.h"
#include "voltron/utility/assertions/precondition.h"

// Concurrency
#include "voltron/utility/concurrency/thread_tracker.h"
#include "voltron/utility/concurrency/mutex_wrapper.h"

// Error Handling
#include "voltron/utility/error/expected_debug.h"
#include "voltron/utility/error/exception_context.h"

// Debugging
#include "voltron/utility/debug/debugger_detection.h"
#include "voltron/utility/debug/hex_dumper.h"

// System
#include "voltron/utility/system/build_info.h"

namespace voltron::utility {

/// @brief Initialize all utility systems (call at startup)
inline void initialize() {
    // Install crash handlers
    crash::SignalHandler::instance().installHandlers();

    // Configure logger defaults
    logging::Logger::instance().setLogLevel(logging::LogLevel::Info);
    logging::Logger::instance().setConsoleOutput(true);
    logging::Logger::instance().setTimestamps(true);

    VOLTRON_LOG_INFO("Voltron 3D Utility System initialized");
}

/// @brief Shutdown utility systems (call before exit)
inline void shutdown() {
    VOLTRON_LOG_INFO("Shutting down Voltron 3D Utility System");

    // Print memory leak report if any
    auto leaks = memory::MemoryTracker::instance().detectLeaks();
    if (!leaks.empty()) {
        VOLTRON_LOG_ERROR("Memory leaks detected!");
        memory::MemoryTracker::instance().printReport(std::cerr);
    }

    // Print thread status
    concurrency::ThreadTracker::instance().printReport(std::cout);

    // Flush logs
    logging::Logger::instance().flush();

    // Restore default signal handlers
    crash::SignalHandler::instance().restoreDefaultHandlers();
}

/// @brief Print full diagnostic report
inline void printDiagnosticReport(std::ostream& os = std::cout) {
    os << "\n";
    os << "╔════════════════════════════════════════╗\n";
    os << "║   VOLTRON 3D DIAGNOSTIC REPORT        ║\n";
    os << "╚════════════════════════════════════════╝\n\n";

    system::BuildInfo::printAll(os);
    os << "\n";

    memory::MemoryTracker::instance().printReport(os);
    os << "\n";

    concurrency::ThreadTracker::instance().printReport(os);
    os << "\n";

    debug::DebuggerDetection::printStatus(os);
    os << "\n";
}

} // namespace voltron::utility
