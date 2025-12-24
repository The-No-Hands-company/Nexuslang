#include <voltron/utility/codegen/template_error_simplifier.h>
#include <iostream>
#include <sstream>

namespace voltron::utility::codegen {

TemplateErrorSimplifier& TemplateErrorSimplifier::instance() {
    static TemplateErrorSimplifier instance;
    return instance;
}

void TemplateErrorSimplifier::initialize(const std::string& config) {
    config_ = config;
    enabled_ = true;
    std::cout << "[TemplateErrorSimplifier] Initialized";
    if (!config.empty()) {
        std::cout << " with config: " << config;
    }
    std::cout << "\n";
}

void TemplateErrorSimplifier::shutdown() {
    enabled_ = false;
    std::cout << "[TemplateErrorSimplifier] Shutdown\n";
}

bool TemplateErrorSimplifier::isEnabled() const {
    return enabled_;
}

void TemplateErrorSimplifier::enable() {
    enabled_ = true;
}

void TemplateErrorSimplifier::disable() {
    enabled_ = false;
}

std::string TemplateErrorSimplifier::getStatus() const {
    std::ostringstream oss;
    oss << "TemplateErrorSimplifier - " << (enabled_ ? "Enabled" : "Disabled");
    if (!config_.empty()) {
        oss << " [config: " << config_ << "]";
    }
    return oss.str();
}

void TemplateErrorSimplifier::reset() {
    config_.clear();
    // Reset internal state here
}

} // namespace voltron::utility::codegen
