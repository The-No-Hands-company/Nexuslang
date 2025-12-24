#include <voltron/utility/formal/smt_solver_interface.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::formal {

SmtSolverInterface& SmtSolverInterface::instance() {
    static SmtSolverInterface instance;
    return instance;
}

void SmtSolverInterface::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[SmtSolverInterface] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void SmtSolverInterface::shutdown() {
    enabled_ = false;
    std::cout << "[SmtSolverInterface] Shutdown\n";
}

bool SmtSolverInterface::isEnabled() const {
    return enabled_;
}

void SmtSolverInterface::enable() {
    enabled_ = true;
}

void SmtSolverInterface::disable() {
    enabled_ = false;
}

std::string SmtSolverInterface::getStatus() const {
    std::ostringstream oss;
    oss << "SmtSolverInterface - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void SmtSolverInterface::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::formal
