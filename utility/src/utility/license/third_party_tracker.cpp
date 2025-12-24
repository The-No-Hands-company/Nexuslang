#include <voltron/utility/license/third_party_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::license {

ThirdPartyTracker& ThirdPartyTracker::instance() {
    static ThirdPartyTracker instance;
    return instance;
}

void ThirdPartyTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ThirdPartyTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ThirdPartyTracker::shutdown() {
    enabled_ = false;
    std::cout << "[ThirdPartyTracker] Shutdown\n";
}

bool ThirdPartyTracker::isEnabled() const {
    return enabled_;
}

void ThirdPartyTracker::enable() {
    enabled_ = true;
}

void ThirdPartyTracker::disable() {
    enabled_ = false;
}

std::string ThirdPartyTracker::getStatus() const {
    std::ostringstream oss;
    oss << "ThirdPartyTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ThirdPartyTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::license
