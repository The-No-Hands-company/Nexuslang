#pragma once

#include <string>
#include <vector>

namespace voltron::utility::error {

/**
 * @brief Centralized error reporting
 * 
 * TODO: Implement comprehensive error_reporter functionality
 */
class ErrorReporter {
public:
    static ErrorReporter& instance();

    /**
     * @brief Initialize error_reporter
     */
    void initialize();

    /**
     * @brief Shutdown error_reporter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ErrorReporter() = default;
    ~ErrorReporter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::error
