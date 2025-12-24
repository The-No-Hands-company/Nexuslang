#include <voltron/utility/interop/c_api_wrapper_debug.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

CApiWrapperDebug& CApiWrapperDebug::instance() {
    static CApiWrapperDebug instance;
    return instance;
}

void CApiWrapperDebug::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CApiWrapperDebug] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CApiWrapperDebug::shutdown() {
    enabled_ = false;
    std::cout << "[CApiWrapperDebug] Shutdown\n";
}

bool CApiWrapperDebug::isEnabled() const {
    return enabled_;
}

void CApiWrapperDebug::enable() {
    enabled_ = true;
}

void CApiWrapperDebug::disable() {
    enabled_ = false;
}

std::string CApiWrapperDebug::getStatus() const {
    std::ostringstream oss;
    oss << "CApiWrapperDebug - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CApiWrapperDebug::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
