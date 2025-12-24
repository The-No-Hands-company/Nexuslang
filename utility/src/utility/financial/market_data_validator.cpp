#include <voltron/utility/financial/market_data_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

MarketDataValidator& MarketDataValidator::instance() {
    static MarketDataValidator instance;
    return instance;
}

void MarketDataValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MarketDataValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MarketDataValidator::shutdown() {
    enabled_ = false;
    std::cout << "[MarketDataValidator] Shutdown\n";
}

bool MarketDataValidator::isEnabled() const {
    return enabled_;
}

void MarketDataValidator::enable() {
    enabled_ = true;
}

void MarketDataValidator::disable() {
    enabled_ = false;
}

std::string MarketDataValidator::getStatus() const {
    std::ostringstream oss;
    oss << "MarketDataValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MarketDataValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
