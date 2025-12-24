#pragma once

#include <string>
#include <vector>

namespace voltron::utility::config {

/**
 * @brief Notify on config changes
 * 
 * TODO: Implement comprehensive config_change_notifier functionality
 */
class ConfigChangeNotifier {
public:
    static ConfigChangeNotifier& instance();

    /**
     * @brief Initialize config_change_notifier
     */
    void initialize();

    /**
     * @brief Shutdown config_change_notifier
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ConfigChangeNotifier() = default;
    ~ConfigChangeNotifier() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::config
