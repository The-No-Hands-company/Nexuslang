#pragma once

#include <string>
#include <vector>

namespace voltron::utility::sanitizer {

/**
 * @brief MemorySanitizer init tracking
 * 
 * TODO: Implement comprehensive msan_helpers functionality
 */
class MsanHelpers {
public:
    static MsanHelpers& instance();

    /**
     * @brief Initialize msan_helpers
     */
    void initialize();

    /**
     * @brief Shutdown msan_helpers
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MsanHelpers() = default;
    ~MsanHelpers() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::sanitizer
