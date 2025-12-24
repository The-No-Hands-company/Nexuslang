#include <voltron/utility/i18n/rtl_layout_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

RtlLayoutValidator& RtlLayoutValidator::instance() {
    static RtlLayoutValidator instance;
    return instance;
}

void RtlLayoutValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RtlLayoutValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RtlLayoutValidator::shutdown() {
    enabled_ = false;
    std::cout << "[RtlLayoutValidator] Shutdown\n";
}

bool RtlLayoutValidator::isEnabled() const {
    return enabled_;
}

void RtlLayoutValidator::enable() {
    enabled_ = true;
}

void RtlLayoutValidator::disable() {
    enabled_ = false;
}

std::string RtlLayoutValidator::getStatus() const {
    std::ostringstream oss;
    oss << "RtlLayoutValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RtlLayoutValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
