#include <voltron/utility/container/cgroup_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::container {

CgroupValidator& CgroupValidator::instance() {
    static CgroupValidator instance;
    return instance;
}

void CgroupValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CgroupValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CgroupValidator::shutdown() {
    enabled_ = false;
    std::cout << "[CgroupValidator] Shutdown\n";
}

bool CgroupValidator::isEnabled() const {
    return enabled_;
}

void CgroupValidator::enable() {
    enabled_ = true;
}

void CgroupValidator::disable() {
    enabled_ = false;
}

std::string CgroupValidator::getStatus() const {
    std::ostringstream oss;
    oss << "CgroupValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CgroupValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::container
