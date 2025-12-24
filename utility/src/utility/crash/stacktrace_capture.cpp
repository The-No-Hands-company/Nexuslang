#include "voltron/utility/crash/stacktrace_capture.h"

namespace voltron::utility::crash {

std::stacktrace StackTraceCapture::capture(size_t skip_frames, size_t max_depth) {
    return std::stacktrace::current(skip_frames, max_depth);
}

std::string StackTraceCapture::format(const std::stacktrace& trace) {
    std::ostringstream oss;
    oss << trace;
    return oss.str();
}

std::string StackTraceCapture::captureAndFormat(size_t skip_frames, size_t max_depth) {
    auto trace = capture(skip_frames + 1, max_depth);  // +1 to skip this function
    return format(trace);
}

} // namespace voltron::utility::crash
