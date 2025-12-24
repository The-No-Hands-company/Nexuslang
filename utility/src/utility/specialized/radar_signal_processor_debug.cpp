#include <voltron/utility/specialized/radar_signal_processor_debug.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::specialized {

RadarSignalProcessorDebug& RadarSignalProcessorDebug::instance() {
    static RadarSignalProcessorDebug instance;
    return instance;
}

void RadarSignalProcessorDebug::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[RadarSignalProcessorDebug] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void RadarSignalProcessorDebug::shutdown() {
    enabled_ = false;
    std::cout << "[RadarSignalProcessorDebug] Shutdown\n";
}

bool RadarSignalProcessorDebug::isEnabled() const {
    return enabled_;
}

void RadarSignalProcessorDebug::enable() {
    enabled_ = true;
}

void RadarSignalProcessorDebug::disable() {
    enabled_ = false;
}

std::string RadarSignalProcessorDebug::getStatus() const {
    std::ostringstream oss;
    oss << "RadarSignalProcessorDebug - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void RadarSignalProcessorDebug::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::specialized
