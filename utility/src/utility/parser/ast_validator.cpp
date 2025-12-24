#include <voltron/utility/parser/ast_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::parser {

AstValidator& AstValidator::instance() {
    static AstValidator instance;
    return instance;
}

void AstValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AstValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AstValidator::shutdown() {
    enabled_ = false;
    std::cout << "[AstValidator] Shutdown\n";
}

bool AstValidator::isEnabled() const {
    return enabled_;
}

void AstValidator::enable() {
    enabled_ = true;
}

void AstValidator::disable() {
    enabled_ = false;
}

std::string AstValidator::getStatus() const {
    std::ostringstream oss;
    oss << "AstValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AstValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::parser
