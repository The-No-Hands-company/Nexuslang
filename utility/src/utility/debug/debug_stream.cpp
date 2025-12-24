#include <voltron/utility/debug/debug_stream.h>
#include <iostream>

namespace voltron::utility::debug {

DebugStream& DebugStream::instance() {
    static DebugStream instance;
    return instance;
}

void DebugStream::initialize() {
    enabled_ = true;
    std::cout << "[DebugStream] Initialized\n";
}

void DebugStream::shutdown() {
    enabled_ = false;
    std::cout << "[DebugStream] Shutdown\n";
}

bool DebugStream::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::debug
