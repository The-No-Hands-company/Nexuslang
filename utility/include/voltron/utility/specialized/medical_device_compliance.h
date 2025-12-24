#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::specialized {

/**
 * @brief Medical device compliance helpers
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Specialized
 * @version 1.0.0
 */
class MedicalDeviceCompliance {
public:
    /**
     * @brief Get singleton instance
     */
    static MedicalDeviceCompliance& instance();

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
    MedicalDeviceCompliance() = default;
    ~MedicalDeviceCompliance() = default;
    
    // Non-copyable, non-movable
    MedicalDeviceCompliance(const MedicalDeviceCompliance&) = delete;
    MedicalDeviceCompliance& operator=(const MedicalDeviceCompliance&) = delete;
    MedicalDeviceCompliance(MedicalDeviceCompliance&&) = delete;
    MedicalDeviceCompliance& operator=(MedicalDeviceCompliance&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::specialized
