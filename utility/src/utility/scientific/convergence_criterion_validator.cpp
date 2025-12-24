#include <voltron/utility/scientific/convergence_criterion_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

ConvergenceCriterionValidator& ConvergenceCriterionValidator::instance() {
    static ConvergenceCriterionValidator instance;
    return instance;
}

void ConvergenceCriterionValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ConvergenceCriterionValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ConvergenceCriterionValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ConvergenceCriterionValidator] Shutdown\n";
}

bool ConvergenceCriterionValidator::isEnabled() const {
    return enabled_;
}

void ConvergenceCriterionValidator::enable() {
    enabled_ = true;
}

void ConvergenceCriterionValidator::disable() {
    enabled_ = false;
}

std::string ConvergenceCriterionValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ConvergenceCriterionValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ConvergenceCriterionValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
