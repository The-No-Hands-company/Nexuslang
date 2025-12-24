#include <voltron/utility/license/sbom_generator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::license {

SbomGenerator& SbomGenerator::instance() {
    static SbomGenerator instance;
    return instance;
}

void SbomGenerator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SbomGenerator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SbomGenerator::shutdown() {
    enabled_ = false;
    std::cout << "[SbomGenerator] Shutdown\n";
}

bool SbomGenerator::isEnabled() const {
    return enabled_;
}

void SbomGenerator::enable() {
    enabled_ = true;
}

void SbomGenerator::disable() {
    enabled_ = false;
}

std::string SbomGenerator::getStatus() const {
    std::ostringstream oss;
    oss << "SbomGenerator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SbomGenerator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::license
