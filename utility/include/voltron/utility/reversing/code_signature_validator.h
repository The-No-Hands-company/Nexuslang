#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::reversing {

/**
 * @brief Validate code signatures
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Reversing
 * @version 1.0.0
 */
class CodeSignatureValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static CodeSignatureValidator& instance();

    /**
     * @brief Initialize the utility
     * @param config Optional configuration parameters
     */
    void initialize(const std::string& config = "");

    /**
     * @brief Shutdown the utility and cleanup resources
     */
    void shutdown();

    /**
     * @brief Check if the utility is currently enabled
     */
    bool isEnabled() const;

    /**
     * @brief Enable the utility
     */
    void enable();

    /**
     * @brief Disable the utility
     */
    void disable();

    /**
     * @brief Get utility statistics/status
     */
    std::string getStatus() const;

    /**
     * @brief Reset utility state
     */
    void reset();

private:
    CodeSignatureValidator() = default;
    ~CodeSignatureValidator() = default;
    
    // Non-copyable, non-movable
    CodeSignatureValidator(const CodeSignatureValidator&) = delete;
    CodeSignatureValidator& operator=(const CodeSignatureValidator&) = delete;
    CodeSignatureValidator(CodeSignatureValidator&&) = delete;
    CodeSignatureValidator& operator=(CodeSignatureValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::reversing
