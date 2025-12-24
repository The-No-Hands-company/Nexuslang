#include <voltron/utility/workflow/deprecation_timeline_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

DeprecationTimelineTracker& DeprecationTimelineTracker::instance() {
    static DeprecationTimelineTracker instance;
    return instance;
}

void DeprecationTimelineTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DeprecationTimelineTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DeprecationTimelineTracker::shutdown() {
    enabled_ = false;
    std::cout << "[DeprecationTimelineTracker] Shutdown\n";
}

bool DeprecationTimelineTracker::isEnabled() const {
    return enabled_;
}

void DeprecationTimelineTracker::enable() {
    enabled_ = true;
}

void DeprecationTimelineTracker::disable() {
    enabled_ = false;
}

std::string DeprecationTimelineTracker::getStatus() const {
    std::ostringstream oss;
    oss << "DeprecationTimelineTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DeprecationTimelineTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
