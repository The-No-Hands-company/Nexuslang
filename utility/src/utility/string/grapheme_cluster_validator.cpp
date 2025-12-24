#include <voltron/utility/string/grapheme_cluster_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::string {

GraphemeClusterValidator& GraphemeClusterValidator::instance() {
    static GraphemeClusterValidator instance;
    return instance;
}

void GraphemeClusterValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[GraphemeClusterValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void GraphemeClusterValidator::shutdown() {
    enabled_ = false;
    std::cout << "[GraphemeClusterValidator] Shutdown\n";
}

bool GraphemeClusterValidator::isEnabled() const {
    return enabled_;
}

void GraphemeClusterValidator::enable() {
    enabled_ = true;
}

void GraphemeClusterValidator::disable() {
    enabled_ = false;
}

std::string GraphemeClusterValidator::getStatus() const {
    std::ostringstream oss;
    oss << "GraphemeClusterValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void GraphemeClusterValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::string
