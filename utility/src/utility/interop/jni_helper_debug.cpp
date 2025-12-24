#include <voltron/utility/interop/jni_helper_debug.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::interop {

JniHelperDebug& JniHelperDebug::instance() {
    static JniHelperDebug instance;
    return instance;
}

void JniHelperDebug::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[JniHelperDebug] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void JniHelperDebug::shutdown() {
    enabled_ = false;
    std::cout << "[JniHelperDebug] Shutdown\n";
}

bool JniHelperDebug::isEnabled() const {
    return enabled_;
}

void JniHelperDebug::enable() {
    enabled_ = true;
}

void JniHelperDebug::disable() {
    enabled_ = false;
}

std::string JniHelperDebug::getStatus() const {
    std::ostringstream oss;
    oss << "JniHelperDebug - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void JniHelperDebug::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::interop
