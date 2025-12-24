#include <voltron/utility/plugin/plugin_version_checker.h>
#include <iostream>

namespace voltron::utility::plugin {

PluginVersionChecker& PluginVersionChecker::instance() {
    static PluginVersionChecker instance;
    return instance;
}

void PluginVersionChecker::initialize() {
    enabled_ = true;
}

void PluginVersionChecker::shutdown() {
    enabled_ = false;
}

bool PluginVersionChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
