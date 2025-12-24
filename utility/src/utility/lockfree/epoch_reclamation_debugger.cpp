#include <voltron/utility/lockfree/epoch_reclamation_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::lockfree {

EpochReclamationDebugger& EpochReclamationDebugger::instance() {
    static EpochReclamationDebugger instance;
    return instance;
}

void EpochReclamationDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[EpochReclamationDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void EpochReclamationDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[EpochReclamationDebugger] Shutdown\n";
}

bool EpochReclamationDebugger::isEnabled() const {
    return enabled_;
}

void EpochReclamationDebugger::enable() {
    enabled_ = true;
}

void EpochReclamationDebugger::disable() {
    enabled_ = false;
}

std::string EpochReclamationDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "EpochReclamationDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void EpochReclamationDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::lockfree
