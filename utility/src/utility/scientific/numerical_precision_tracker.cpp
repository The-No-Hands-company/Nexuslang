#include <voltron/utility/scientific/numerical_precision_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

NumericalPrecisionTracker& NumericalPrecisionTracker::instance() {
    static NumericalPrecisionTracker instance;
    return instance;
}

void NumericalPrecisionTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[NumericalPrecisionTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void NumericalPrecisionTracker::shutdown() {
    enabled_ = false;
    std::cout << "[NumericalPrecisionTracker] Shutdown\n";
}

bool NumericalPrecisionTracker::isEnabled() const {
    return enabled_;
}

void NumericalPrecisionTracker::enable() {
    enabled_ = true;
}

void NumericalPrecisionTracker::disable() {
    enabled_ = false;
}

std::string NumericalPrecisionTracker::getStatus() const {
    std::ostringstream oss;
    oss << "NumericalPrecisionTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void NumericalPrecisionTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
