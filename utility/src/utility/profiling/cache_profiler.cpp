#include <voltron/utility/profiling/cache_profiler.h>
#include <iostream>

namespace voltron::utility::profiling {

CacheProfiler& CacheProfiler::instance() {
    static CacheProfiler instance;
    return instance;
}

void CacheProfiler::initialize() {
    enabled_ = true;
    std::cout << "[CacheProfiler] Initialized\n";
}

void CacheProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[CacheProfiler] Shutdown\n";
}

bool CacheProfiler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::profiling
