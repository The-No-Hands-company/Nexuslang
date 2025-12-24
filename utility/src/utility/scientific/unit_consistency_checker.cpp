#include <voltron/utility/scientific/unit_consistency_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

UnitConsistencyChecker& UnitConsistencyChecker::instance() {
    static UnitConsistencyChecker instance;
    return instance;
}

void UnitConsistencyChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[UnitConsistencyChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void UnitConsistencyChecker::shutdown() {
    enabled_ = false;
    std::cout << "[UnitConsistencyChecker] Shutdown\n";
}

bool UnitConsistencyChecker::isEnabled() const {
    return enabled_;
}

void UnitConsistencyChecker::enable() {
    enabled_ = true;
}

void UnitConsistencyChecker::disable() {
    enabled_ = false;
}

std::string UnitConsistencyChecker::getStatus() const {
    std::ostringstream oss;
    oss << "UnitConsistencyChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void UnitConsistencyChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
