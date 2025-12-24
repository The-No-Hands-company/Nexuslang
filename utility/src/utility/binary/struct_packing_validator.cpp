#include <voltron/utility/binary/struct_packing_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

StructPackingValidator& StructPackingValidator::instance() {
    static StructPackingValidator instance;
    return instance;
}

void StructPackingValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[StructPackingValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void StructPackingValidator::shutdown() {
    enabled_ = false;
    std::cout << "[StructPackingValidator] Shutdown\n";
}

bool StructPackingValidator::isEnabled() const {
    return enabled_;
}

void StructPackingValidator::enable() {
    enabled_ = true;
}

void StructPackingValidator::disable() {
    enabled_ = false;
}

std::string StructPackingValidator::getStatus() const {
    std::ostringstream oss;
    oss << "StructPackingValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void StructPackingValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
