#include <voltron/utility/parser/ir_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

IrValidator& IrValidator::instance() {
    static IrValidator instance;
    return instance;
}

void IrValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[IrValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void IrValidator::shutdown() {
    enabled_ = false;
    std::cout << "[IrValidator] Shutdown\n";
}

bool IrValidator::isEnabled() const {
    return enabled_;
}

void IrValidator::enable() {
    enabled_ = true;
}

void IrValidator::disable() {
    enabled_ = false;
}

std::string IrValidator::getStatus() const {
    std::ostringstream oss;
    oss << "IrValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void IrValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
