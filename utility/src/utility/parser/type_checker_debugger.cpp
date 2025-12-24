#include <voltron/utility/parser/type_checker_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

TypeCheckerDebugger& TypeCheckerDebugger::instance() {
    static TypeCheckerDebugger instance;
    return instance;
}

void TypeCheckerDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TypeCheckerDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TypeCheckerDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[TypeCheckerDebugger] Shutdown\n";
}

bool TypeCheckerDebugger::isEnabled() const {
    return enabled_;
}

void TypeCheckerDebugger::enable() {
    enabled_ = true;
}

void TypeCheckerDebugger::disable() {
    enabled_ = false;
}

std::string TypeCheckerDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "TypeCheckerDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TypeCheckerDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
