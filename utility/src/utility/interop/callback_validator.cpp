#include <voltron/utility/interop/callback_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

CallbackValidator& CallbackValidator::instance() {
    static CallbackValidator instance;
    return instance;
}

void CallbackValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CallbackValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CallbackValidator::shutdown() {
    enabled_ = false;
    std::cout << "[CallbackValidator] Shutdown\n";
}

bool CallbackValidator::isEnabled() const {
    return enabled_;
}

void CallbackValidator::enable() {
    enabled_ = true;
}

void CallbackValidator::disable() {
    enabled_ = false;
}

std::string CallbackValidator::getStatus() const {
    std::ostringstream oss;
    oss << "CallbackValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CallbackValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
