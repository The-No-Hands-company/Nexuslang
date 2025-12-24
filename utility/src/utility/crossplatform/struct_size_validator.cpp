#include <voltron/utility/crossplatform/struct_size_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

StructSizeValidator& StructSizeValidator::instance() {
    static StructSizeValidator instance;
    return instance;
}

void StructSizeValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StructSizeValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StructSizeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[StructSizeValidator] Shutdown\n";
}

bool StructSizeValidator::isEnabled() const {
    return enabled_;
}

void StructSizeValidator::enable() {
    enabled_ = true;
}

void StructSizeValidator::disable() {
    enabled_ = false;
}

std::string StructSizeValidator::getStatus() const {
    std::ostringstream oss;
    oss << "StructSizeValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StructSizeValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
