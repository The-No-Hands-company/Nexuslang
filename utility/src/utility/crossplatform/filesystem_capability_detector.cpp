#include <voltron/utility/crossplatform/filesystem_capability_detector.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::crossplatform {

FilesystemCapabilityDetector& FilesystemCapabilityDetector::instance() {
    static FilesystemCapabilityDetector instance;
    return instance;
}

void FilesystemCapabilityDetector::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[FilesystemCapabilityDetector] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void FilesystemCapabilityDetector::shutdown() {
    enabled_ = false;
    std::cout << "[FilesystemCapabilityDetector] Shutdown\n";
}

bool FilesystemCapabilityDetector::isEnabled() const {
    return enabled_;
}

void FilesystemCapabilityDetector::enable() {
    enabled_ = true;
}

void FilesystemCapabilityDetector::disable() {
    enabled_ = false;
}

std::string FilesystemCapabilityDetector::getStatus() const {
    std::ostringstream oss;
    oss << "FilesystemCapabilityDetector - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void FilesystemCapabilityDetector::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::crossplatform
