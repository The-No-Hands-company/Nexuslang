#include <voltron/utility/allocator/pool_allocator_monitor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

PoolAllocatorMonitor& PoolAllocatorMonitor::instance() {
    static PoolAllocatorMonitor instance;
    return instance;
}

void PoolAllocatorMonitor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PoolAllocatorMonitor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PoolAllocatorMonitor::shutdown() {
    enabled_ = false;
    std::cout << "[PoolAllocatorMonitor] Shutdown\n";
}

bool PoolAllocatorMonitor::isEnabled() const {
    return enabled_;
}

void PoolAllocatorMonitor::enable() {
    enabled_ = true;
}

void PoolAllocatorMonitor::disable() {
    enabled_ = false;
}

std::string PoolAllocatorMonitor::getStatus() const {
    std::ostringstream oss;
    oss << "PoolAllocatorMonitor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PoolAllocatorMonitor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
