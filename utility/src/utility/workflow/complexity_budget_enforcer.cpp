#include <voltron/utility/workflow/complexity_budget_enforcer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

ComplexityBudgetEnforcer& ComplexityBudgetEnforcer::instance() {
    static ComplexityBudgetEnforcer instance;
    return instance;
}

void ComplexityBudgetEnforcer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ComplexityBudgetEnforcer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ComplexityBudgetEnforcer::shutdown() {
    enabled_ = false;
    std::cout << "[ComplexityBudgetEnforcer] Shutdown\n";
}

bool ComplexityBudgetEnforcer::isEnabled() const {
    return enabled_;
}

void ComplexityBudgetEnforcer::enable() {
    enabled_ = true;
}

void ComplexityBudgetEnforcer::disable() {
    enabled_ = false;
}

std::string ComplexityBudgetEnforcer::getStatus() const {
    std::ostringstream oss;
    oss << "ComplexityBudgetEnforcer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ComplexityBudgetEnforcer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
