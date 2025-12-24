#include <voltron/utility/legacy/encoding_converter_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::legacy {

EncodingConverterValidator& EncodingConverterValidator::instance() {
    static EncodingConverterValidator instance;
    return instance;
}

void EncodingConverterValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EncodingConverterValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EncodingConverterValidator::shutdown() {
    enabled_ = false;
    std::cout << "[EncodingConverterValidator] Shutdown\n";
}

bool EncodingConverterValidator::isEnabled() const {
    return enabled_;
}

void EncodingConverterValidator::enable() {
    enabled_ = true;
}

void EncodingConverterValidator::disable() {
    enabled_ = false;
}

std::string EncodingConverterValidator::getStatus() const {
    std::ostringstream oss;
    oss << "EncodingConverterValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EncodingConverterValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::legacy
