#include <voltron/utility/specialized/aerospace_certification_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

AerospaceCertificationHelper& AerospaceCertificationHelper::instance() {
    static AerospaceCertificationHelper instance;
    return instance;
}

void AerospaceCertificationHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AerospaceCertificationHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AerospaceCertificationHelper::shutdown() {
    enabled_ = false;
    std::cout << "[AerospaceCertificationHelper] Shutdown\n";
}

bool AerospaceCertificationHelper::isEnabled() const {
    return enabled_;
}

void AerospaceCertificationHelper::enable() {
    enabled_ = true;
}

void AerospaceCertificationHelper::disable() {
    enabled_ = false;
}

std::string AerospaceCertificationHelper::getStatus() const {
    std::ostringstream oss;
    oss << "AerospaceCertificationHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AerospaceCertificationHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
