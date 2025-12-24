#include <voltron/utility/interop/python_binding_debug.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

PythonBindingDebug& PythonBindingDebug::instance() {
    static PythonBindingDebug instance;
    return instance;
}

void PythonBindingDebug::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PythonBindingDebug] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PythonBindingDebug::shutdown() {
    enabled_ = false;
    std::cout << "[PythonBindingDebug] Shutdown\n";
}

bool PythonBindingDebug::isEnabled() const {
    return enabled_;
}

void PythonBindingDebug::enable() {
    enabled_ = true;
}

void PythonBindingDebug::disable() {
    enabled_ = false;
}

std::string PythonBindingDebug::getStatus() const {
    std::ostringstream oss;
    oss << "PythonBindingDebug - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PythonBindingDebug::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
