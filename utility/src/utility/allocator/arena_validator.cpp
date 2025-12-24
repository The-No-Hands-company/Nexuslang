#include <voltron/utility/allocator/arena_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::allocator {

ArenaValidator& ArenaValidator::instance() {
    static ArenaValidator instance;
    return instance;
}

void ArenaValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ArenaValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ArenaValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ArenaValidator] Shutdown\n";
}

bool ArenaValidator::isEnabled() const {
    return enabled_;
}

void ArenaValidator::enable() {
    enabled_ = true;
}

void ArenaValidator::disable() {
    enabled_ = false;
}

std::string ArenaValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ArenaValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ArenaValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::allocator
