#include <voltron/utility/workflow/tech_debt_marker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

TechDebtMarker& TechDebtMarker::instance() {
    static TechDebtMarker instance;
    return instance;
}

void TechDebtMarker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TechDebtMarker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TechDebtMarker::shutdown() {
    enabled_ = false;
    std::cout << "[TechDebtMarker] Shutdown\n";
}

bool TechDebtMarker::isEnabled() const {
    return enabled_;
}

void TechDebtMarker::enable() {
    enabled_ = true;
}

void TechDebtMarker::disable() {
    enabled_ = false;
}

std::string TechDebtMarker::getStatus() const {
    std::ostringstream oss;
    oss << "TechDebtMarker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TechDebtMarker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
