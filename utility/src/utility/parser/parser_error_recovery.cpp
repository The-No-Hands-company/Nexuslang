#include <voltron/utility/parser/parser_error_recovery.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

ParserErrorRecovery& ParserErrorRecovery::instance() {
    static ParserErrorRecovery instance;
    return instance;
}

void ParserErrorRecovery::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ParserErrorRecovery] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ParserErrorRecovery::shutdown() {
    enabled_ = false;
    std::cout << "[ParserErrorRecovery] Shutdown\n";
}

bool ParserErrorRecovery::isEnabled() const {
    return enabled_;
}

void ParserErrorRecovery::enable() {
    enabled_ = true;
}

void ParserErrorRecovery::disable() {
    enabled_ = false;
}

std::string ParserErrorRecovery::getStatus() const {
    std::ostringstream oss;
    oss << "ParserErrorRecovery - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ParserErrorRecovery::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
