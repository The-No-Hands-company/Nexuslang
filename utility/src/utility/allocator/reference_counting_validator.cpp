#include <voltron/utility/allocator/reference_counting_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

ReferenceCountingValidator& ReferenceCountingValidator::instance() {
    static ReferenceCountingValidator instance;
    return instance;
}

void ReferenceCountingValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ReferenceCountingValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ReferenceCountingValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ReferenceCountingValidator] Shutdown\n";
}

bool ReferenceCountingValidator::isEnabled() const {
    return enabled_;
}

void ReferenceCountingValidator::enable() {
    enabled_ = true;
}

void ReferenceCountingValidator::disable() {
    enabled_ = false;
}

std::string ReferenceCountingValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ReferenceCountingValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ReferenceCountingValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
