#include "voltron/utility/crash/signal_handler.h"
#include "voltron/utility/crash/stacktrace_capture.h"
#include <iostream>
#include <cstring>

namespace voltron::utility::crash {

SignalHandler& SignalHandler::instance() {
    static SignalHandler handler;
    return handler;
}

void SignalHandler::installHandlers() {
    if (handlers_installed_) return;

    std::signal(SIGSEGV, handleSignal);  // Segmentation fault
    std::signal(SIGABRT, handleSignal);  // Abort
    std::signal(SIGFPE, handleSignal);   // Floating-point exception
    std::signal(SIGILL, handleSignal);   // Illegal instruction

    handlers_installed_ = true;
}

void SignalHandler::setCrashCallback(CrashCallback callback) {
    crash_callback_ = std::move(callback);
}

void SignalHandler::restoreDefaultHandlers() {
    std::signal(SIGSEGV, SIG_DFL);
    std::signal(SIGABRT, SIG_DFL);
    std::signal(SIGFPE, SIG_DFL);
    std::signal(SIGILL, SIG_DFL);

    handlers_installed_ = false;
}

void SignalHandler::handleSignal(int signal) {
    // This is a signal handler - must be signal-safe!
    // Limited to async-signal-safe functions only

    const char* signal_name = "UNKNOWN";
    switch (signal) {
        case SIGSEGV: signal_name = "SIGSEGV (Segmentation fault)"; break;
        case SIGABRT: signal_name = "SIGABRT (Abort)"; break;
        case SIGFPE:  signal_name = "SIGFPE (Floating-point exception)"; break;
        case SIGILL:  signal_name = "SIGILL (Illegal instruction)"; break;
    }

    // Minimal async-signal-safe output
    std::cerr << "\n=== FATAL SIGNAL RECEIVED ===\n";
    std::cerr << "Signal: " << signal_name << " (" << signal << ")\n";

    // Attempt stack trace (may not be signal-safe in all implementations)
    try {
        auto trace = StackTraceCapture::captureAndFormat(1);
        std::cerr << "Stack trace:\n" << trace << "\n";
    } catch (...) {
        std::cerr << "Failed to capture stack trace\n";
    }

    // Invoke callback if set
    auto& handler = instance();
    if (handler.crash_callback_) {
        try {
            handler.crash_callback_(signal, signal_name);
        } catch (...) {
            std::cerr << "Crash callback threw exception\n";
        }
    }

    std::cerr << "===========================\n";

    // Restore default handler and re-raise to generate core dump
    std::signal(signal, SIG_DFL);
    std::raise(signal);
}

} // namespace voltron::utility::crash
