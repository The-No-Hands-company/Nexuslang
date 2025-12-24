#include <voltron/utility/formal/proof_obligation_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

ProofObligationTracker& ProofObligationTracker::instance() {
    static ProofObligationTracker instance;
    return instance;
}

void ProofObligationTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ProofObligationTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ProofObligationTracker::shutdown() {
    enabled_ = false;
    std::cout << "[ProofObligationTracker] Shutdown\n";
}

bool ProofObligationTracker::isEnabled() const {
    return enabled_;
}

void ProofObligationTracker::enable() {
    enabled_ = true;
}

void ProofObligationTracker::disable() {
    enabled_ = false;
}

std::string ProofObligationTracker::getStatus() const {
    std::ostringstream oss;
    oss << "ProofObligationTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ProofObligationTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
