#include <voltron/utility/plugin/plugin_crash_isolator.h>
#include <iostream>

namespace voltron::utility::plugin {

PluginCrashIsolator& PluginCrashIsolator::instance() {
    static PluginCrashIsolator instance;
    return instance;
}

void PluginCrashIsolator::initialize() {
    enabled_ = true;
}

void PluginCrashIsolator::shutdown() {
    enabled_ = false;
}

bool PluginCrashIsolator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
