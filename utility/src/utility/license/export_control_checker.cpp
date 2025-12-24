#include <voltron/utility/license/export_control_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::license {

ExportControlChecker& ExportControlChecker::instance() {
    static ExportControlChecker instance;
    return instance;
}

void ExportControlChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ExportControlChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ExportControlChecker::shutdown() {
    enabled_ = false;
    std::cout << "[ExportControlChecker] Shutdown\n";
}

bool ExportControlChecker::isEnabled() const {
    return enabled_;
}

void ExportControlChecker::enable() {
    enabled_ = true;
}

void ExportControlChecker::disable() {
    enabled_ = false;
}

std::string ExportControlChecker::getStatus() const {
    std::ostringstream oss;
    oss << "ExportControlChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ExportControlChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::license
