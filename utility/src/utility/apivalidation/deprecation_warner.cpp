#include <voltron/utility/apivalidation/deprecation_warner.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

DeprecationWarner& DeprecationWarner::instance() {
    static DeprecationWarner instance;
    return instance;
}

void DeprecationWarner::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DeprecationWarner] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DeprecationWarner::shutdown() {
    enabled_ = false;
    std::cout << "[DeprecationWarner] Shutdown\n";
}

bool DeprecationWarner::isEnabled() const {
    return enabled_;
}

void DeprecationWarner::enable() {
    enabled_ = true;
}

void DeprecationWarner::disable() {
    enabled_ = false;
}

std::string DeprecationWarner::getStatus() const {
    std::ostringstream oss;
    oss << "DeprecationWarner - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DeprecationWarner::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
