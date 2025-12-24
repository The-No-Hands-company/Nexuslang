#include <voltron/utility/concurrency/thread_local_storage_debug.h>
#include <iostream>

namespace voltron::utility::concurrency {

ThreadLocalStorageDebug& ThreadLocalStorageDebug::instance() {
    static ThreadLocalStorageDebug instance;
    return instance;
}

void ThreadLocalStorageDebug::initialize() {
    enabled_ = true;
    std::cout << "[ThreadLocalStorageDebug] Initialized\n";
}

void ThreadLocalStorageDebug::shutdown() {
    enabled_ = false;
    std::cout << "[ThreadLocalStorageDebug] Shutdown\n";
}

bool ThreadLocalStorageDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::concurrency
