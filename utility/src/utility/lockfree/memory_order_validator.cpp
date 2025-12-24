#include <voltron/utility/lockfree/memory_order_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::lockfree {

MemoryOrderValidator& MemoryOrderValidator::instance() {
    static MemoryOrderValidator instance;
    return instance;
}

void MemoryOrderValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MemoryOrderValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MemoryOrderValidator::shutdown() {
    enabled_ = false;
    std::cout << "[MemoryOrderValidator] Shutdown\n";
}

bool MemoryOrderValidator::isEnabled() const {
    return enabled_;
}

void MemoryOrderValidator::enable() {
    enabled_ = true;
}

void MemoryOrderValidator::disable() {
    enabled_ = false;
}

std::string MemoryOrderValidator::getStatus() const {
    std::ostringstream oss;
    oss << "MemoryOrderValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MemoryOrderValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::lockfree
