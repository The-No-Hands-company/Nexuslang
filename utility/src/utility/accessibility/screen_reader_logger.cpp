#include <voltron/utility/accessibility/screen_reader_logger.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::accessibility {

ScreenReaderLogger& ScreenReaderLogger::instance() {
    static ScreenReaderLogger instance;
    return instance;
}

void ScreenReaderLogger::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ScreenReaderLogger] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ScreenReaderLogger::shutdown() {
    enabled_ = false;
    std::cout << "[ScreenReaderLogger] Shutdown\n";
}

bool ScreenReaderLogger::isEnabled() const {
    return enabled_;
}

void ScreenReaderLogger::enable() {
    enabled_ = true;
}

void ScreenReaderLogger::disable() {
    enabled_ = false;
}

std::string ScreenReaderLogger::getStatus() const {
    std::ostringstream oss;
    oss << "ScreenReaderLogger - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ScreenReaderLogger::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::accessibility
