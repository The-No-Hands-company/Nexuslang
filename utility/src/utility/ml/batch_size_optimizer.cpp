#include <voltron/utility/ml/batch_size_optimizer.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::ml {

BatchSizeOptimizer& BatchSizeOptimizer::instance() {
    static BatchSizeOptimizer instance;
    return instance;
}

void BatchSizeOptimizer::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[BatchSizeOptimizer] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void BatchSizeOptimizer::shutdown() {
    enabled_ = false;
    std::cout << "[BatchSizeOptimizer] Shutdown\n";
}

bool BatchSizeOptimizer::isEnabled() const {
    return enabled_;
}

void BatchSizeOptimizer::enable() {
    enabled_ = true;
}

void BatchSizeOptimizer::disable() {
    enabled_ = false;
}

std::string BatchSizeOptimizer::getStatus() const {
    std::ostringstream oss;
    oss << "BatchSizeOptimizer - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void BatchSizeOptimizer::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::ml
