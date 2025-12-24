#include <voltron/utility/financial/trade_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

TradeValidator& TradeValidator::instance() {
    static TradeValidator instance;
    return instance;
}

void TradeValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TradeValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TradeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[TradeValidator] Shutdown\n";
}

bool TradeValidator::isEnabled() const {
    return enabled_;
}

void TradeValidator::enable() {
    enabled_ = true;
}

void TradeValidator::disable() {
    enabled_ = false;
}

std::string TradeValidator::getStatus() const {
    std::ostringstream oss;
    oss << "TradeValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TradeValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
