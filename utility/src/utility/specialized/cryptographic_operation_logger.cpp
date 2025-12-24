#include <voltron/utility/specialized/cryptographic_operation_logger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

CryptographicOperationLogger& CryptographicOperationLogger::instance() {
    static CryptographicOperationLogger instance;
    return instance;
}

void CryptographicOperationLogger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CryptographicOperationLogger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CryptographicOperationLogger::shutdown() {
    enabled_ = false;
    std::cout << "[CryptographicOperationLogger] Shutdown\n";
}

bool CryptographicOperationLogger::isEnabled() const {
    return enabled_;
}

void CryptographicOperationLogger::enable() {
    enabled_ = true;
}

void CryptographicOperationLogger::disable() {
    enabled_ = false;
}

std::string CryptographicOperationLogger::getStatus() const {
    std::ostringstream oss;
    oss << "CryptographicOperationLogger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CryptographicOperationLogger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
