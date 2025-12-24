#include <voltron/utility/workflow/style_guide_enforcer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

StyleGuideEnforcer& StyleGuideEnforcer::instance() {
    static StyleGuideEnforcer instance;
    return instance;
}

void StyleGuideEnforcer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StyleGuideEnforcer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StyleGuideEnforcer::shutdown() {
    enabled_ = false;
    std::cout << "[StyleGuideEnforcer] Shutdown\n";
}

bool StyleGuideEnforcer::isEnabled() const {
    return enabled_;
}

void StyleGuideEnforcer::enable() {
    enabled_ = true;
}

void StyleGuideEnforcer::disable() {
    enabled_ = false;
}

std::string StyleGuideEnforcer::getStatus() const {
    std::ostringstream oss;
    oss << "StyleGuideEnforcer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StyleGuideEnforcer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
