#include <voltron/utility/codegen/preprocessor_tracer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

PreprocessorTracer& PreprocessorTracer::instance() {
    static PreprocessorTracer instance;
    return instance;
}

void PreprocessorTracer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[PreprocessorTracer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void PreprocessorTracer::shutdown() {
    enabled_ = false;
    std::cout << "[PreprocessorTracer] Shutdown\n";
}

bool PreprocessorTracer::isEnabled() const {
    return enabled_;
}

void PreprocessorTracer::enable() {
    enabled_ = true;
}

void PreprocessorTracer::disable() {
    enabled_ = false;
}

std::string PreprocessorTracer::getStatus() const {
    std::ostringstream oss;
    oss << "PreprocessorTracer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void PreprocessorTracer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
