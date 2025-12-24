#pragma once

#include <string>
#include <vector>

namespace voltron::utility::cpp23 {

/**
 * @brief Debug explicit object parameters
 * 
 * TODO: Implement comprehensive deducing_this_helper functionality
 */
class DeducingThisHelper {
public:
    static DeducingThisHelper& instance();

    /**
     * @brief Initialize deducing_this_helper
     */
    void initialize();

    /**
     * @brief Shutdown deducing_this_helper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DeducingThisHelper() = default;
    ~DeducingThisHelper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::cpp23
