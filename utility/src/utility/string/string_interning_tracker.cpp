#include <voltron/utility/string/string_interning_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

StringInterningTracker& StringInterningTracker::instance() {
    static StringInterningTracker instance;
    return instance;
}

void StringInterningTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StringInterningTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StringInterningTracker::shutdown() {
    enabled_ = false;
    std::cout << "[StringInterningTracker] Shutdown\n";
}

bool StringInterningTracker::isEnabled() const {
    return enabled_;
}

void StringInterningTracker::enable() {
    enabled_ = true;
}

void StringInterningTracker::disable() {
    enabled_ = false;
}

std::string StringInterningTracker::getStatus() const {
    std::ostringstream oss;
    oss << "StringInterningTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StringInterningTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
