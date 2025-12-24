#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::crossplatform {

/**
 * @brief Normalize line endings
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Crossplatform
 * @version 1.0.0
 */
class LineEndingNormalizer {
public:
    /**
     * @brief Get singleton instance
     */
    static LineEndingNormalizer& instance();

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
    LineEndingNormalizer() = default;
    ~LineEndingNormalizer() = default;
    
    // Non-copyable, non-movable
    LineEndingNormalizer(const LineEndingNormalizer&) = delete;
    LineEndingNormalizer& operator=(const LineEndingNormalizer&) = delete;
    LineEndingNormalizer(LineEndingNormalizer&&) = delete;
    LineEndingNormalizer& operator=(LineEndingNormalizer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::crossplatform
