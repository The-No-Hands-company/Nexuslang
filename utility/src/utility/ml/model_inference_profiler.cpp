#include <voltron/utility/ml/model_inference_profiler.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::ml {

ModelInferenceProfiler& ModelInferenceProfiler::instance() {
    static ModelInferenceProfiler instance;
    return instance;
}

void ModelInferenceProfiler::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ModelInferenceProfiler] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ModelInferenceProfiler::shutdown() {
    enabled_ = false;
    std::cout << "[ModelInferenceProfiler] Shutdown\n";
}

bool ModelInferenceProfiler::isEnabled() const {
    return enabled_;
}

void ModelInferenceProfiler::enable() {
    enabled_ = true;
}

void ModelInferenceProfiler::disable() {
    enabled_ = false;
}

std::string ModelInferenceProfiler::getStatus() const {
    std::ostringstream oss;
    oss << "ModelInferenceProfiler - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ModelInferenceProfiler::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::ml
