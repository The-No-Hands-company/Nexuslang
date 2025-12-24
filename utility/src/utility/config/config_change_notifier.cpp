#include <voltron/utility/config/config_change_notifier.h>
#include <iostream>

namespace voltron::utility::config {

ConfigChangeNotifier& ConfigChangeNotifier::instance() {
    static ConfigChangeNotifier instance;
    return instance;
}

void ConfigChangeNotifier::initialize() {
    enabled_ = true;
    std::cout << "[ConfigChangeNotifier] Initialized\n";
}

void ConfigChangeNotifier::shutdown() {
    enabled_ = false;
    std::cout << "[ConfigChangeNotifier] Shutdown\n";
}

bool ConfigChangeNotifier::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
