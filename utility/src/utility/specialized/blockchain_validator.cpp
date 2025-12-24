#include <voltron/utility/specialized/blockchain_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

BlockchainValidator& BlockchainValidator::instance() {
    static BlockchainValidator instance;
    return instance;
}

void BlockchainValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BlockchainValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BlockchainValidator::shutdown() {
    enabled_ = false;
    std::cout << "[BlockchainValidator] Shutdown\n";
}

bool BlockchainValidator::isEnabled() const {
    return enabled_;
}

void BlockchainValidator::enable() {
    enabled_ = true;
}

void BlockchainValidator::disable() {
    enabled_ = false;
}

std::string BlockchainValidator::getStatus() const {
    std::ostringstream oss;
    oss << "BlockchainValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BlockchainValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
