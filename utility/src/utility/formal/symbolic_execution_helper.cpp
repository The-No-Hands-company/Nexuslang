#include <voltron/utility/formal/symbolic_execution_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

SymbolicExecutionHelper& SymbolicExecutionHelper::instance() {
    static SymbolicExecutionHelper instance;
    return instance;
}

void SymbolicExecutionHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SymbolicExecutionHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SymbolicExecutionHelper::shutdown() {
    enabled_ = false;
    std::cout << "[SymbolicExecutionHelper] Shutdown\n";
}

bool SymbolicExecutionHelper::isEnabled() const {
    return enabled_;
}

void SymbolicExecutionHelper::enable() {
    enabled_ = true;
}

void SymbolicExecutionHelper::disable() {
    enabled_ = false;
}

std::string SymbolicExecutionHelper::getStatus() const {
    std::ostringstream oss;
    oss << "SymbolicExecutionHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SymbolicExecutionHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
