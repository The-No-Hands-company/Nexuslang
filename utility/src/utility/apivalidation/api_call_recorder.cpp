#include <voltron/utility/apivalidation/api_call_recorder.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::apivalidation {

ApiCallRecorder& ApiCallRecorder::instance() {
    static ApiCallRecorder instance;
    return instance;
}

void ApiCallRecorder::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ApiCallRecorder] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ApiCallRecorder::shutdown() {
    enabled_ = false;
    std::cout << "[ApiCallRecorder] Shutdown\n";
}

bool ApiCallRecorder::isEnabled() const {
    return enabled_;
}

void ApiCallRecorder::enable() {
    enabled_ = true;
}

void ApiCallRecorder::disable() {
    enabled_ = false;
}

std::string ApiCallRecorder::getStatus() const {
    std::ostringstream oss;
    oss << "ApiCallRecorder - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ApiCallRecorder::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::apivalidation
