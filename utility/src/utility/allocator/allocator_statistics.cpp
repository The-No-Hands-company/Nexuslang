#include <voltron/utility/allocator/allocator_statistics.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

AllocatorStatistics& AllocatorStatistics::instance() {
    static AllocatorStatistics instance;
    return instance;
}

void AllocatorStatistics::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AllocatorStatistics] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AllocatorStatistics::shutdown() {
    enabled_ = false;
    std::cout << "[AllocatorStatistics] Shutdown\n";
}

bool AllocatorStatistics::isEnabled() const {
    return enabled_;
}

void AllocatorStatistics::enable() {
    enabled_ = true;
}

void AllocatorStatistics::disable() {
    enabled_ = false;
}

std::string AllocatorStatistics::getStatus() const {
    std::ostringstream oss;
    oss << "AllocatorStatistics - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AllocatorStatistics::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
