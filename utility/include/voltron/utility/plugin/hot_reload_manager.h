#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Debug hot-reloading code
 */
class HotReloadManager {
public:
    static HotReloadManager& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    HotReloadManager() = default;
    ~HotReloadManager() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
