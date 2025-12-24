#include <voltron/utility/binary/magic_number_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

MagicNumberValidator& MagicNumberValidator::instance() {
    static MagicNumberValidator instance;
    return instance;
}

void MagicNumberValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MagicNumberValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MagicNumberValidator::shutdown() {
    enabled_ = false;
    std::cout << "[MagicNumberValidator] Shutdown\n";
}

bool MagicNumberValidator::isEnabled() const {
    return enabled_;
}

void MagicNumberValidator::enable() {
    enabled_ = true;
}

void MagicNumberValidator::disable() {
    enabled_ = false;
}

std::string MagicNumberValidator::getStatus() const {
    std::ostringstream oss;
    oss << "MagicNumberValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MagicNumberValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
