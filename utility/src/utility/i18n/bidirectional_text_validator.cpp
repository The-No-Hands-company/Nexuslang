#include <voltron/utility/i18n/bidirectional_text_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

BidirectionalTextValidator& BidirectionalTextValidator::instance() {
    static BidirectionalTextValidator instance;
    return instance;
}

void BidirectionalTextValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BidirectionalTextValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BidirectionalTextValidator::shutdown() {
    enabled_ = false;
    std::cout << "[BidirectionalTextValidator] Shutdown\n";
}

bool BidirectionalTextValidator::isEnabled() const {
    return enabled_;
}

void BidirectionalTextValidator::enable() {
    enabled_ = true;
}

void BidirectionalTextValidator::disable() {
    enabled_ = false;
}

std::string BidirectionalTextValidator::getStatus() const {
    std::ostringstream oss;
    oss << "BidirectionalTextValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BidirectionalTextValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
