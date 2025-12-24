#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::i18n {

/**
 * @brief Detect text encoding issues
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category I18n
 * @version 1.0.0
 */
class EncodingDetector {
public:
    /**
     * @brief Get singleton instance
     */
    static EncodingDetector& instance();

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
    EncodingDetector() = default;
    ~EncodingDetector() = default;
    
    // Non-copyable, non-movable
    EncodingDetector(const EncodingDetector&) = delete;
    EncodingDetector& operator=(const EncodingDetector&) = delete;
    EncodingDetector(EncodingDetector&&) = delete;
    EncodingDetector& operator=(EncodingDetector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::i18n
