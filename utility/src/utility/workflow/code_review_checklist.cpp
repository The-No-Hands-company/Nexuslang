#include <voltron/utility/workflow/code_review_checklist.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::workflow {

CodeReviewChecklist& CodeReviewChecklist::instance() {
    static CodeReviewChecklist instance;
    return instance;
}

void CodeReviewChecklist::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[CodeReviewChecklist] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void CodeReviewChecklist::shutdown() {
    enabled_ = false;
    std::cout << "[CodeReviewChecklist] Shutdown\n";
}

bool CodeReviewChecklist::isEnabled() const {
    return enabled_;
}

void CodeReviewChecklist::enable() {
    enabled_ = true;
}

void CodeReviewChecklist::disable() {
    enabled_ = false;
}

std::string CodeReviewChecklist::getStatus() const {
    std::ostringstream oss;
    oss << "CodeReviewChecklist - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void CodeReviewChecklist::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::workflow
