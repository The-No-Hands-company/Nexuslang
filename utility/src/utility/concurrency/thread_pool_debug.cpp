#include <voltron/utility/concurrency/thread_pool_debug.h>
#include <iostream>

namespace voltron::utility::concurrency {

ThreadPoolDebug& ThreadPoolDebug::instance() {
    static ThreadPoolDebug instance;
    return instance;
}

void ThreadPoolDebug::initialize() {
    enabled_ = true;
    std::cout << "[ThreadPoolDebug] Initialized\n";
}

void ThreadPoolDebug::shutdown() {
    enabled_ = false;
    std::cout << "[ThreadPoolDebug] Shutdown\n";
}

bool ThreadPoolDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
