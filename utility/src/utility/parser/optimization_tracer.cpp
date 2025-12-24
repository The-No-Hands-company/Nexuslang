#include <voltron/utility/parser/optimization_tracer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

OptimizationTracer& OptimizationTracer::instance() {
    static OptimizationTracer instance;
    return instance;
}

void OptimizationTracer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[OptimizationTracer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void OptimizationTracer::shutdown() {
    enabled_ = false;
    std::cout << "[OptimizationTracer] Shutdown\n";
}

bool OptimizationTracer::isEnabled() const {
    return enabled_;
}

void OptimizationTracer::enable() {
    enabled_ = true;
}

void OptimizationTracer::disable() {
    enabled_ = false;
}

std::string OptimizationTracer::getStatus() const {
    std::ostringstream oss;
    oss << "OptimizationTracer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void OptimizationTracer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
