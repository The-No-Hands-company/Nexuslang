#include <voltron/utility/cloud/instance_metadata_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

InstanceMetadataValidator& InstanceMetadataValidator::instance() {
    static InstanceMetadataValidator instance;
    return instance;
}

void InstanceMetadataValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[InstanceMetadataValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void InstanceMetadataValidator::shutdown() {
    enabled_ = false;
    std::cout << "[InstanceMetadataValidator] Shutdown\n";
}

bool InstanceMetadataValidator::isEnabled() const {
    return enabled_;
}

void InstanceMetadataValidator::enable() {
    enabled_ = true;
}

void InstanceMetadataValidator::disable() {
    enabled_ = false;
}

std::string InstanceMetadataValidator::getStatus() const {
    std::ostringstream oss;
    oss << "InstanceMetadataValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void InstanceMetadataValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
