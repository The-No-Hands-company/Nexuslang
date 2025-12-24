#pragma once

#include <csignal>
#include <functional>
#include <string>

namespace voltron::utility::crash {

/// @brief Signal handler for crash diagnostics
class SignalHandler {
public:
    using CrashCallback = std::function<void(int signal, const std::string& info)>;

    static SignalHandler& instance();

    /// Install signal handlers for crash signals
    void installHandlers();

    /// Set callback to be invoked on crash
    void setCrashCallback(CrashCallback callback);

    /// Restore default signal handlers
    void restoreDefaultHandlers();

private:
    SignalHandler() = default;

    SignalHandler(const SignalHandler&) = delete;
    SignalHandler& operator=(const SignalHandler&) = delete;

    static void handleSignal(int signal);

    CrashCallback crash_callback_;
    bool handlers_installed_ = false;
};

} // namespace voltron::utility::crash
