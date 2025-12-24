#include <voltron/utility/specialized/medical_device_compliance.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

MedicalDeviceCompliance& MedicalDeviceCompliance::instance() {
    static MedicalDeviceCompliance instance;
    return instance;
}

void MedicalDeviceCompliance::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[MedicalDeviceCompliance] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void MedicalDeviceCompliance::shutdown() {
    enabled_ = false;
    std::cout << "[MedicalDeviceCompliance] Shutdown\n";
}

bool MedicalDeviceCompliance::isEnabled() const {
    return enabled_;
}

void MedicalDeviceCompliance::enable() {
    enabled_ = true;
}

void MedicalDeviceCompliance::disable() {
    enabled_ = false;
}

std::string MedicalDeviceCompliance::getStatus() const {
    std::ostringstream oss;
    oss << "MedicalDeviceCompliance - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void MedicalDeviceCompliance::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
