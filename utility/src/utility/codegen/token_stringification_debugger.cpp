#include <voltron/utility/codegen/token_stringification_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

TokenStringificationDebugger& TokenStringificationDebugger::instance() {
    static TokenStringificationDebugger instance;
    return instance;
}

void TokenStringificationDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TokenStringificationDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TokenStringificationDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[TokenStringificationDebugger] Shutdown\n";
}

bool TokenStringificationDebugger::isEnabled() const {
    return enabled_;
}

void TokenStringificationDebugger::enable() {
    enabled_ = true;
}

void TokenStringificationDebugger::disable() {
    enabled_ = false;
}

std::string TokenStringificationDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "TokenStringificationDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TokenStringificationDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
