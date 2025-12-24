#include <voltron/utility/interop/wasm_interface_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

WasmInterfaceValidator& WasmInterfaceValidator::instance() {
    static WasmInterfaceValidator instance;
    return instance;
}

void WasmInterfaceValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[WasmInterfaceValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void WasmInterfaceValidator::shutdown() {
    enabled_ = false;
    std::cout << "[WasmInterfaceValidator] Shutdown\n";
}

bool WasmInterfaceValidator::isEnabled() const {
    return enabled_;
}

void WasmInterfaceValidator::enable() {
    enabled_ = true;
}

void WasmInterfaceValidator::disable() {
    enabled_ = false;
}

std::string WasmInterfaceValidator::getStatus() const {
    std::ostringstream oss;
    oss << "WasmInterfaceValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void WasmInterfaceValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
