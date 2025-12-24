#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::specialized {

/**
 * @brief Validate DSP algorithms
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Specialized
 * @version 1.0.0
 */
class DspAlgorithmValidator {
public:
    /**
     * @brief Get singleton instance
     */
    static DspAlgorithmValidator& instance();

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
    DspAlgorithmValidator() = default;
    ~DspAlgorithmValidator() = default;
    
    // Non-copyable, non-movable
    DspAlgorithmValidator(const DspAlgorithmValidator&) = delete;
    DspAlgorithmValidator& operator=(const DspAlgorithmValidator&) = delete;
    DspAlgorithmValidator(DspAlgorithmValidator&&) = delete;
    DspAlgorithmValidator& operator=(DspAlgorithmValidator&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::specialized
