#pragma once

#include <string>
#include <vector>

namespace voltron::utility::security {

/**
 * @brief Properly clear sensitive data
 * 
 * TODO: Implement comprehensive secure_wipe functionality
 */
class SecureWipe {
public:
    static SecureWipe& instance();

    /**
     * @brief Initialize secure_wipe
     */
    void initialize();

    /**
     * @brief Shutdown secure_wipe
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SecureWipe() = default;
    ~SecureWipe() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::security
