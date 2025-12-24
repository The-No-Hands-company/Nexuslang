#include <voltron/utility/scientific/matrix_condition_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

MatrixConditionChecker& MatrixConditionChecker::instance() {
    static MatrixConditionChecker instance;
    return instance;
}

void MatrixConditionChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MatrixConditionChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MatrixConditionChecker::shutdown() {
    enabled_ = false;
    std::cout << "[MatrixConditionChecker] Shutdown\n";
}

bool MatrixConditionChecker::isEnabled() const {
    return enabled_;
}

void MatrixConditionChecker::enable() {
    enabled_ = true;
}

void MatrixConditionChecker::disable() {
    enabled_ = false;
}

std::string MatrixConditionChecker::getStatus() const {
    std::ostringstream oss;
    oss << "MatrixConditionChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MatrixConditionChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
