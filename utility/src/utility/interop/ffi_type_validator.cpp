#include <voltron/utility/interop/ffi_type_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

FfiTypeValidator& FfiTypeValidator::instance() {
    static FfiTypeValidator instance;
    return instance;
}

void FfiTypeValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FfiTypeValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FfiTypeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[FfiTypeValidator] Shutdown\n";
}

bool FfiTypeValidator::isEnabled() const {
    return enabled_;
}

void FfiTypeValidator::enable() {
    enabled_ = true;
}

void FfiTypeValidator::disable() {
    enabled_ = false;
}

std::string FfiTypeValidator::getStatus() const {
    std::ostringstream oss;
    oss << "FfiTypeValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FfiTypeValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
