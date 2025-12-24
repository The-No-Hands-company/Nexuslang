#include <voltron/utility/protocol/checksum_calculator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::protocol {

ChecksumCalculator& ChecksumCalculator::instance() {
    static ChecksumCalculator instance;
    return instance;
}

void ChecksumCalculator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ChecksumCalculator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ChecksumCalculator::shutdown() {
    enabled_ = false;
    std::cout << "[ChecksumCalculator] Shutdown\n";
}

bool ChecksumCalculator::isEnabled() const {
    return enabled_;
}

void ChecksumCalculator::enable() {
    enabled_ = true;
}

void ChecksumCalculator::disable() {
    enabled_ = false;
}

std::string ChecksumCalculator::getStatus() const {
    std::ostringstream oss;
    oss << "ChecksumCalculator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ChecksumCalculator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::protocol
