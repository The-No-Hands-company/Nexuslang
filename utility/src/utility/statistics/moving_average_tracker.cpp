#include <voltron/utility/statistics/moving_average_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::statistics {

MovingAverageTracker& MovingAverageTracker::instance() {
    static MovingAverageTracker instance;
    return instance;
}

void MovingAverageTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MovingAverageTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MovingAverageTracker::shutdown() {
    enabled_ = false;
    std::cout << "[MovingAverageTracker] Shutdown\n";
}

bool MovingAverageTracker::isEnabled() const {
    return enabled_;
}

void MovingAverageTracker::enable() {
    enabled_ = true;
}

void MovingAverageTracker::disable() {
    enabled_ = false;
}

std::string MovingAverageTracker::getStatus() const {
    std::ostringstream oss;
    oss << "MovingAverageTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MovingAverageTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::statistics
