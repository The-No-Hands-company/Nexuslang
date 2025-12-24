#include <voltron/utility/i18n/collation_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::i18n {

CollationDebugger& CollationDebugger::instance() {
    static CollationDebugger instance;
    return instance;
}

void CollationDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CollationDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CollationDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[CollationDebugger] Shutdown\n";
}

bool CollationDebugger::isEnabled() const {
    return enabled_;
}

void CollationDebugger::enable() {
    enabled_ = true;
}

void CollationDebugger::disable() {
    enabled_ = false;
}

std::string CollationDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "CollationDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CollationDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::i18n
