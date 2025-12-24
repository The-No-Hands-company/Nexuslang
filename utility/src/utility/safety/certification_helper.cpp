#include <voltron/utility/safety/certification_helper.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::safety {

CertificationHelper& CertificationHelper::instance() {
    static CertificationHelper instance;
    return instance;
}

void CertificationHelper::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CertificationHelper] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CertificationHelper::shutdown() {
    enabled_ = false;
    std::cout << "[CertificationHelper] Shutdown\n";
}

bool CertificationHelper::isEnabled() const {
    return enabled_;
}

void CertificationHelper::enable() {
    enabled_ = true;
}

void CertificationHelper::disable() {
    enabled_ = false;
}

std::string CertificationHelper::getStatus() const {
    std::ostringstream oss;
    oss << "CertificationHelper - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CertificationHelper::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::safety
