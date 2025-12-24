#include <voltron/utility/specialized/fpga_interface_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

FpgaInterfaceDebugger& FpgaInterfaceDebugger::instance() {
    static FpgaInterfaceDebugger instance;
    return instance;
}

void FpgaInterfaceDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FpgaInterfaceDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FpgaInterfaceDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[FpgaInterfaceDebugger] Shutdown\n";
}

bool FpgaInterfaceDebugger::isEnabled() const {
    return enabled_;
}

void FpgaInterfaceDebugger::enable() {
    enabled_ = true;
}

void FpgaInterfaceDebugger::disable() {
    enabled_ = false;
}

std::string FpgaInterfaceDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "FpgaInterfaceDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FpgaInterfaceDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
