#include <voltron/utility/documentation/api_documentation_validator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::documentation {

ApiDocumentationValidator& ApiDocumentationValidator::instance() {
    static ApiDocumentationValidator instance;
    return instance;
}

void ApiDocumentationValidator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[ApiDocumentationValidator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void ApiDocumentationValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ApiDocumentationValidator] Shutdown\n";
}

bool ApiDocumentationValidator::isEnabled() const {
    return enabled_;
}

void ApiDocumentationValidator::enable() {
    enabled_ = true;
}

void ApiDocumentationValidator::disable() {
    enabled_ = false;
}

std::string ApiDocumentationValidator::getStatus() const {
    std::ostringstream oss;
    oss << "ApiDocumentationValidator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void ApiDocumentationValidator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::documentation
