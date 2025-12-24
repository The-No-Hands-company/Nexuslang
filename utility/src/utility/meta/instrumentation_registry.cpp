#include <voltron/utility/meta/instrumentation_registry.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::meta {

InstrumentationRegistry& InstrumentationRegistry::instance() {
    static InstrumentationRegistry instance;
    return instance;
}

void InstrumentationRegistry::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[InstrumentationRegistry] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void InstrumentationRegistry::shutdown() {
    enabled_ = false;
    std::cout << "[InstrumentationRegistry] Shutdown\n";
}

bool InstrumentationRegistry::isEnabled() const {
    return enabled_;
}

void InstrumentationRegistry::enable() {
    enabled_ = true;
}

void InstrumentationRegistry::disable() {
    enabled_ = false;
}

std::string InstrumentationRegistry::getStatus() const {
    std::ostringstream oss;
    oss << "InstrumentationRegistry - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void InstrumentationRegistry::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::meta
