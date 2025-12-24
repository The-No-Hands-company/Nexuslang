#include <voltron/utility/lockfree/linearizability_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::lockfree {

LinearizabilityChecker& LinearizabilityChecker::instance() {
    static LinearizabilityChecker instance;
    return instance;
}

void LinearizabilityChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[LinearizabilityChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void LinearizabilityChecker::shutdown() {
    enabled_ = false;
    std::cout << "[LinearizabilityChecker] Shutdown\n";
}

bool LinearizabilityChecker::isEnabled() const {
    return enabled_;
}

void LinearizabilityChecker::enable() {
    enabled_ = true;
}

void LinearizabilityChecker::disable() {
    enabled_ = false;
}

std::string LinearizabilityChecker::getStatus() const {
    std::ostringstream oss;
    oss << "LinearizabilityChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void LinearizabilityChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::lockfree
