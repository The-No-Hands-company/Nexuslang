#pragma once

#include <string>
#include <vector>

namespace voltron::utility::security {

/**
 * @brief Generic input validation
 * 
 * TODO: Implement comprehensive input_sanitizer functionality
 */
class InputSanitizer {
public:
    static InputSanitizer& instance();

    /**
     * @brief Initialize input_sanitizer
     */
    void initialize();

    /**
     * @brief Shutdown input_sanitizer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    InputSanitizer() = default;
    ~InputSanitizer() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::security
