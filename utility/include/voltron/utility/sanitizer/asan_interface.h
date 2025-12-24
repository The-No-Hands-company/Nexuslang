#pragma once

#include <string>
#include <vector>

namespace voltron::utility::sanitizer {

/**
 * @brief AddressSanitizer manual poisoning
 * 
 * TODO: Implement comprehensive asan_interface functionality
 */
class AsanInterface {
public:
    static AsanInterface& instance();

    /**
     * @brief Initialize asan_interface
     */
    void initialize();

    /**
     * @brief Shutdown asan_interface
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    AsanInterface() = default;
    ~AsanInterface() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::sanitizer
