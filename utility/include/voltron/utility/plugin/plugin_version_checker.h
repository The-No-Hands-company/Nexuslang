#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Check plugin versions
 */
class PluginVersionChecker {
public:
    static PluginVersionChecker& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    PluginVersionChecker() = default;
    ~PluginVersionChecker() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
