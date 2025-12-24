#pragma once

#include <stacktrace>
#include <string>
#include <sstream>

namespace voltron::utility::crash {

/// @brief Capture and format stack trace (C++23)
class StackTraceCapture {
public:
    /// Capture current stack trace, skipping N frames
    static std::stacktrace capture(size_t skip_frames = 0, size_t max_depth = 50);

    /// Format stack trace as string
    static std::string format(const std::stacktrace& trace);

    /// Capture and format in one call
    static std::string captureAndFormat(size_t skip_frames = 1, size_t max_depth = 50);
};

} // namespace voltron::utility::crash
