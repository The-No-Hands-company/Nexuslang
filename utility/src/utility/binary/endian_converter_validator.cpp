#include <voltron/utility/binary/endian_converter_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

EndianConverterValidator& EndianConverterValidator::instance() {
    static EndianConverterValidator instance;
    return instance;
}

void EndianConverterValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EndianConverterValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EndianConverterValidator::shutdown() {
    enabled_ = false;
    std::cout << "[EndianConverterValidator] Shutdown\n";
}

bool EndianConverterValidator::isEnabled() const {
    return enabled_;
}

void EndianConverterValidator::enable() {
    enabled_ = true;
}

void EndianConverterValidator::disable() {
    enabled_ = false;
}

std::string EndianConverterValidator::getStatus() const {
    std::ostringstream oss;
    oss << "EndianConverterValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EndianConverterValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
