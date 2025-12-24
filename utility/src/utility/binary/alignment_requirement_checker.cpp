#include <voltron/utility/binary/alignment_requirement_checker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::binary {

AlignmentRequirementChecker& AlignmentRequirementChecker::instance() {
    static AlignmentRequirementChecker instance;
    return instance;
}

void AlignmentRequirementChecker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AlignmentRequirementChecker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AlignmentRequirementChecker::shutdown() {
    enabled_ = false;
    std::cout << "[AlignmentRequirementChecker] Shutdown\n";
}

bool AlignmentRequirementChecker::isEnabled() const {
    return enabled_;
}

void AlignmentRequirementChecker::enable() {
    enabled_ = true;
}

void AlignmentRequirementChecker::disable() {
    enabled_ = false;
}

std::string AlignmentRequirementChecker::getStatus() const {
    std::ostringstream oss;
    oss << "AlignmentRequirementChecker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AlignmentRequirementChecker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::binary
