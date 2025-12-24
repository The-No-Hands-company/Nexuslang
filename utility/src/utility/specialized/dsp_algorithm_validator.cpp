#include <voltron/utility/specialized/dsp_algorithm_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

DspAlgorithmValidator& DspAlgorithmValidator::instance() {
    static DspAlgorithmValidator instance;
    return instance;
}

void DspAlgorithmValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[DspAlgorithmValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void DspAlgorithmValidator::shutdown() {
    enabled_ = false;
    std::cout << "[DspAlgorithmValidator] Shutdown\n";
}

bool DspAlgorithmValidator::isEnabled() const {
    return enabled_;
}

void DspAlgorithmValidator::enable() {
    enabled_ = true;
}

void DspAlgorithmValidator::disable() {
    enabled_ = false;
}

std::string DspAlgorithmValidator::getStatus() const {
    std::ostringstream oss;
    oss << "DspAlgorithmValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void DspAlgorithmValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
