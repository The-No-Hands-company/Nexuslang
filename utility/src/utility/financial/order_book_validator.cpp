#include <voltron/utility/financial/order_book_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::financial {

OrderBookValidator& OrderBookValidator::instance() {
    static OrderBookValidator instance;
    return instance;
}

void OrderBookValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[OrderBookValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void OrderBookValidator::shutdown() {
    enabled_ = false;
    std::cout << "[OrderBookValidator] Shutdown\n";
}

bool OrderBookValidator::isEnabled() const {
    return enabled_;
}

void OrderBookValidator::enable() {
    enabled_ = true;
}

void OrderBookValidator::disable() {
    enabled_ = false;
}

std::string OrderBookValidator::getStatus() const {
    std::ostringstream oss;
    oss << "OrderBookValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void OrderBookValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::financial
