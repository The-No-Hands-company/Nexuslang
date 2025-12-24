#include <voltron/utility/string/utf8_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

Utf8Validator& Utf8Validator::instance() {
    static Utf8Validator instance;
    return instance;
}

void Utf8Validator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[Utf8Validator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void Utf8Validator::shutdown() {
    enabled_ = false;
    std::cout << "[Utf8Validator] Shutdown\n";
}

bool Utf8Validator::isEnabled() const {
    return enabled_;
}

void Utf8Validator::enable() {
    enabled_ = true;
}

void Utf8Validator::disable() {
    enabled_ = false;
}

std::string Utf8Validator::getStatus() const {
    std::ostringstream oss;
    oss << "Utf8Validator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void Utf8Validator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
