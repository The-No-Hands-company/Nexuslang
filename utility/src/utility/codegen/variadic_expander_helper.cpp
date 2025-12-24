#include <voltron/utility/codegen/variadic_expander_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

VariadicExpanderHelper& VariadicExpanderHelper::instance() {
    static VariadicExpanderHelper instance;
    return instance;
}

void VariadicExpanderHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[VariadicExpanderHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void VariadicExpanderHelper::shutdown() {
    enabled_ = false;
    std::cout << "[VariadicExpanderHelper] Shutdown\n";
}

bool VariadicExpanderHelper::isEnabled() const {
    return enabled_;
}

void VariadicExpanderHelper::enable() {
    enabled_ = true;
}

void VariadicExpanderHelper::disable() {
    enabled_ = false;
}

std::string VariadicExpanderHelper::getStatus() const {
    std::ostringstream oss;
    oss << "VariadicExpanderHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void VariadicExpanderHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
