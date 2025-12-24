#include <voltron/utility/config/plugin_validator.h>
#include <iostream>

namespace voltron::utility::config {

PluginValidator& PluginValidator::instance() {
    static PluginValidator instance;
    return instance;
}

void PluginValidator::initialize() {
    enabled_ = true;
    std::cout << "[PluginValidator] Initialized\n";
}

void PluginValidator::shutdown() {
    enabled_ = false;
    std::cout << "[PluginValidator] Shutdown\n";
}

bool PluginValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
