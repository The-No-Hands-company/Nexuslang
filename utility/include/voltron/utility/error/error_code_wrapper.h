#pragma once

#include <string>
#include <vector>

namespace voltron::utility::error {

/**
 * @brief Enhanced std::error_code with context
 * 
 * TODO: Implement comprehensive error_code_wrapper functionality
 */
class ErrorCodeWrapper {
public:
    static ErrorCodeWrapper& instance();

    /**
     * @brief Initialize error_code_wrapper
     */
    void initialize();

    /**
     * @brief Shutdown error_code_wrapper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ErrorCodeWrapper() = default;
    ~ErrorCodeWrapper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::error
