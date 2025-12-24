#include <voltron/utility/codegen/macro_hygiene_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

MacroHygieneChecker& MacroHygieneChecker::instance() {
    static MacroHygieneChecker instance;
    return instance;
}

void MacroHygieneChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MacroHygieneChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MacroHygieneChecker::shutdown() {
    enabled_ = false;
    std::cout << "[MacroHygieneChecker] Shutdown\n";
}

bool MacroHygieneChecker::isEnabled() const {
    return enabled_;
}

void MacroHygieneChecker::enable() {
    enabled_ = true;
}

void MacroHygieneChecker::disable() {
    enabled_ = false;
}

std::string MacroHygieneChecker::getStatus() const {
    std::ostringstream oss;
    oss << "MacroHygieneChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MacroHygieneChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
