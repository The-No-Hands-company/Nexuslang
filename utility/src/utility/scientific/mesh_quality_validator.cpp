#include <voltron/utility/scientific/mesh_quality_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

MeshQualityValidator& MeshQualityValidator::instance() {
    static MeshQualityValidator instance;
    return instance;
}

void MeshQualityValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MeshQualityValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MeshQualityValidator::shutdown() {
    enabled_ = false;
    std::cout << "[MeshQualityValidator] Shutdown\n";
}

bool MeshQualityValidator::isEnabled() const {
    return enabled_;
}

void MeshQualityValidator::enable() {
    enabled_ = true;
}

void MeshQualityValidator::disable() {
    enabled_ = false;
}

std::string MeshQualityValidator::getStatus() const {
    std::ostringstream oss;
    oss << "MeshQualityValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MeshQualityValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
