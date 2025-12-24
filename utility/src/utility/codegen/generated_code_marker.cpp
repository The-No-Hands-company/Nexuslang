#include <voltron/utility/codegen/generated_code_marker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

GeneratedCodeMarker& GeneratedCodeMarker::instance() {
    static GeneratedCodeMarker instance;
    return instance;
}

void GeneratedCodeMarker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[GeneratedCodeMarker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void GeneratedCodeMarker::shutdown() {
    enabled_ = false;
    std::cout << "[GeneratedCodeMarker] Shutdown\n";
}

bool GeneratedCodeMarker::isEnabled() const {
    return enabled_;
}

void GeneratedCodeMarker::enable() {
    enabled_ = true;
}

void GeneratedCodeMarker::disable() {
    enabled_ = false;
}

std::string GeneratedCodeMarker::getStatus() const {
    std::ostringstream oss;
    oss << "GeneratedCodeMarker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void GeneratedCodeMarker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
