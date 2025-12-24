#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::license {

/**
 * @brief Generate Software Bill of Materials
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category License
 * @version 1.0.0
 */
class SbomGenerator {
public:
    /**
     * @brief Get singleton instance
     */
    static SbomGenerator& instance();

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
    SbomGenerator() = default;
    ~SbomGenerator() = default;
    
    // Non-copyable, non-movable
    SbomGenerator(const SbomGenerator&) = delete;
    SbomGenerator& operator=(const SbomGenerator&) = delete;
    SbomGenerator(SbomGenerator&&) = delete;
    SbomGenerator& operator=(SbomGenerator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::license
