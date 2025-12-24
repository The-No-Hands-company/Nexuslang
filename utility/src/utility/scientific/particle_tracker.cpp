#include <voltron/utility/scientific/particle_tracker.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

ParticleTracker& ParticleTracker::instance() {
    static ParticleTracker instance;
    return instance;
}

void ParticleTracker::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ParticleTracker] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ParticleTracker::shutdown() {
    enabled_ = false;
    std::cout << "[ParticleTracker] Shutdown\n";
}

bool ParticleTracker::isEnabled() const {
    return enabled_;
}

void ParticleTracker::enable() {
    enabled_ = true;
}

void ParticleTracker::disable() {
    enabled_ = false;
}

std::string ParticleTracker::getStatus() const {
    std::ostringstream oss;
    oss << "ParticleTracker - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ParticleTracker::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
