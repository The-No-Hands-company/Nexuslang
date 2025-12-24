#include <voltron/utility/codegen/code_generator_debugger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

CodeGeneratorDebugger& CodeGeneratorDebugger::instance() {
    static CodeGeneratorDebugger instance;
    return instance;
}

void CodeGeneratorDebugger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CodeGeneratorDebugger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CodeGeneratorDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[CodeGeneratorDebugger] Shutdown\n";
}

bool CodeGeneratorDebugger::isEnabled() const {
    return enabled_;
}

void CodeGeneratorDebugger::enable() {
    enabled_ = true;
}

void CodeGeneratorDebugger::disable() {
    enabled_ = false;
}

std::string CodeGeneratorDebugger::getStatus() const {
    std::ostringstream oss;
    oss << "CodeGeneratorDebugger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CodeGeneratorDebugger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
