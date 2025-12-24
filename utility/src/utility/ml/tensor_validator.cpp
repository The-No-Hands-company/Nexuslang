#include <voltron/utility/ml/tensor_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::ml {

TensorValidator& TensorValidator::instance() {
    static TensorValidator instance;
    return instance;
}

void TensorValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TensorValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TensorValidator::shutdown() {
    enabled_ = false;
    std::cout << "[TensorValidator] Shutdown\n";
}

bool TensorValidator::isEnabled() const {
    return enabled_;
}

void TensorValidator::enable() {
    enabled_ = true;
}

void TensorValidator::disable() {
    enabled_ = false;
}

std::string TensorValidator::getStatus() const {
    std::ostringstream oss;
    oss << "TensorValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TensorValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::ml
