#include <voltron/utility/workflow/todo_extractor.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

TodoExtractor& TodoExtractor::instance() {
    static TodoExtractor instance;
    return instance;
}

void TodoExtractor::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TodoExtractor] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TodoExtractor::shutdown() {
    enabled_ = false;
    std::cout << "[TodoExtractor] Shutdown\n";
}

bool TodoExtractor::isEnabled() const {
    return enabled_;
}

void TodoExtractor::enable() {
    enabled_ = true;
}

void TodoExtractor::disable() {
    enabled_ = false;
}

std::string TodoExtractor::getStatus() const {
    std::ostringstream oss;
    oss << "TodoExtractor - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TodoExtractor::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
