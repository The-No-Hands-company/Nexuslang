#include <voltron/utility/lockfree/compare_exchange_tracer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::lockfree {

CompareExchangeTracer& CompareExchangeTracer::instance() {
    static CompareExchangeTracer instance;
    return instance;
}

void CompareExchangeTracer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CompareExchangeTracer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CompareExchangeTracer::shutdown() {
    enabled_ = false;
    std::cout << "[CompareExchangeTracer] Shutdown\n";
}

bool CompareExchangeTracer::isEnabled() const {
    return enabled_;
}

void CompareExchangeTracer::enable() {
    enabled_ = true;
}

void CompareExchangeTracer::disable() {
    enabled_ = false;
}

std::string CompareExchangeTracer::getStatus() const {
    std::ostringstream oss;
    oss << "CompareExchangeTracer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CompareExchangeTracer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::lockfree
