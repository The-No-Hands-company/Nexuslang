#pragma once

#include <string>
#include <vector>

namespace voltron::utility::sanitizer {

/**
 * @brief UBSan custom handlers
 * 
 * TODO: Implement comprehensive ubsan_handlers functionality
 */
class UbsanHandlers {
public:
    static UbsanHandlers& instance();

    /**
     * @brief Initialize ubsan_handlers
     */
    void initialize();

    /**
     * @brief Shutdown ubsan_handlers
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    UbsanHandlers() = default;
    ~UbsanHandlers() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::sanitizer
