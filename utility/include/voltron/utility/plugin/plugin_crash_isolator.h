#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Isolate plugin crashes
 */
class PluginCrashIsolator {
public:
    static PluginCrashIsolator& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    PluginCrashIsolator() = default;
    ~PluginCrashIsolator() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
