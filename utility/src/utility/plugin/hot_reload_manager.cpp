#include <voltron/utility/plugin/hot_reload_manager.h>
#include <iostream>

namespace voltron::utility::plugin {

HotReloadManager& HotReloadManager::instance() {
    static HotReloadManager instance;
    return instance;
}

void HotReloadManager::initialize() {
    enabled_ = true;
}

void HotReloadManager::shutdown() {
    enabled_ = false;
}

bool HotReloadManager::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::plugin
