#include <voltron/utility/reversing/code_signature_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::reversing {

CodeSignatureValidator& CodeSignatureValidator::instance() {
    static CodeSignatureValidator instance;
    return instance;
}

void CodeSignatureValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CodeSignatureValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CodeSignatureValidator::shutdown() {
    enabled_ = false;
    std::cout << "[CodeSignatureValidator] Shutdown\n";
}

bool CodeSignatureValidator::isEnabled() const {
    return enabled_;
}

void CodeSignatureValidator::enable() {
    enabled_ = true;
}

void CodeSignatureValidator::disable() {
    enabled_ = false;
}

std::string CodeSignatureValidator::getStatus() const {
    std::ostringstream oss;
    oss << "CodeSignatureValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CodeSignatureValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::reversing
