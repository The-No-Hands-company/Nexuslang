#include <voltron/utility/binary/binary_format_fuzzer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

BinaryFormatFuzzer& BinaryFormatFuzzer::instance() {
    static BinaryFormatFuzzer instance;
    return instance;
}

void BinaryFormatFuzzer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BinaryFormatFuzzer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BinaryFormatFuzzer::shutdown() {
    enabled_ = false;
    std::cout << "[BinaryFormatFuzzer] Shutdown\n";
}

bool BinaryFormatFuzzer::isEnabled() const {
    return enabled_;
}

void BinaryFormatFuzzer::enable() {
    enabled_ = true;
}

void BinaryFormatFuzzer::disable() {
    enabled_ = false;
}

std::string BinaryFormatFuzzer::getStatus() const {
    std::ostringstream oss;
    oss << "BinaryFormatFuzzer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BinaryFormatFuzzer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
