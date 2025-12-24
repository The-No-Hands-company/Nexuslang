#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::string {

/**
 * @brief Validate UTF-8 encoding correctness
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category String
 * @version 1.0.0
 */
class Utf8Validator {
public:
    /**
     * @brief Get singleton instance
     */
    static Utf8Validator& instance();

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
    Utf8Validator() = default;
    ~Utf8Validator() = default;
    
    // Non-copyable, non-movable
    Utf8Validator(const Utf8Validator&) = delete;
    Utf8Validator& operator=(const Utf8Validator&) = delete;
    Utf8Validator(Utf8Validator&&) = delete;
    Utf8Validator& operator=(Utf8Validator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::string
