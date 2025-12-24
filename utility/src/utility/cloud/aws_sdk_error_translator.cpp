#include <voltron/utility/cloud/aws_sdk_error_translator.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::cloud {

AwsSdkErrorTranslator& AwsSdkErrorTranslator::instance() {
    static AwsSdkErrorTranslator instance;
    return instance;
}

void AwsSdkErrorTranslator::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[AwsSdkErrorTranslator] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void AwsSdkErrorTranslator::shutdown() {
    enabled_ = false;
    std::cout << "[AwsSdkErrorTranslator] Shutdown\n";
}

bool AwsSdkErrorTranslator::isEnabled() const {
    return enabled_;
}

void AwsSdkErrorTranslator::enable() {
    enabled_ = true;
}

void AwsSdkErrorTranslator::disable() {
    enabled_ = false;
}

std::string AwsSdkErrorTranslator::getStatus() const {
    std::ostringstream oss;
    oss << "AwsSdkErrorTranslator - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void AwsSdkErrorTranslator::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::cloud
