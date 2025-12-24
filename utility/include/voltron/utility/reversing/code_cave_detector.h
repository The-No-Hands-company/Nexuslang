#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::reversing {

/**
 * @brief Detect code modification attempts
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Reversing
 * @version 1.0.0
 */
class CodeCaveDetector {
public:
    /**
     * @brief Get singleton instance
     */
    static CodeCaveDetector& instance();

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
    CodeCaveDetector() = default;
    ~CodeCaveDetector() = default;
    
    // Non-copyable, non-movable
    CodeCaveDetector(const CodeCaveDetector&) = delete;
    CodeCaveDetector& operator=(const CodeCaveDetector&) = delete;
    CodeCaveDetector(CodeCaveDetector&&) = delete;
    CodeCaveDetector& operator=(CodeCaveDetector&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::reversing
