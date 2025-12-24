#include <voltron/utility/apivalidation/return_value_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

ReturnValueChecker& ReturnValueChecker::instance() {
    static ReturnValueChecker instance;
    return instance;
}

void ReturnValueChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ReturnValueChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ReturnValueChecker::shutdown() {
    enabled_ = false;
    std::cout << "[ReturnValueChecker] Shutdown\n";
}

bool ReturnValueChecker::isEnabled() const {
    return enabled_;
}

void ReturnValueChecker::enable() {
    enabled_ = true;
}

void ReturnValueChecker::disable() {
    enabled_ = false;
}

std::string ReturnValueChecker::getStatus() const {
    std::ostringstream oss;
    oss << "ReturnValueChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ReturnValueChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
