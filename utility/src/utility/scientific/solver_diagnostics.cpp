#include <voltron/utility/scientific/solver_diagnostics.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::scientific {

SolverDiagnostics& SolverDiagnostics::instance() {
    static SolverDiagnostics instance;
    return instance;
}

void SolverDiagnostics::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SolverDiagnostics] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SolverDiagnostics::shutdown() {
    enabled_ = false;
    std::cout << "[SolverDiagnostics] Shutdown\n";
}

bool SolverDiagnostics::isEnabled() const {
    return enabled_;
}

void SolverDiagnostics::enable() {
    enabled_ = true;
}

void SolverDiagnostics::disable() {
    enabled_ = false;
}

std::string SolverDiagnostics::getStatus() const {
    std::ostringstream oss;
    oss << "SolverDiagnostics - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SolverDiagnostics::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::scientific
