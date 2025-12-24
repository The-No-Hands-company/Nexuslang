#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::container {

/**
 * @brief Kubernetes liveness/readiness helpers
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Container
 * @version 1.0.0
 */
class KubernetesProbeHelper {
public:
    /**
     * @brief Get singleton instance
     */
    static KubernetesProbeHelper& instance();

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
    KubernetesProbeHelper() = default;
    ~KubernetesProbeHelper() = default;
    
    // Non-copyable, non-movable
    KubernetesProbeHelper(const KubernetesProbeHelper&) = delete;
    KubernetesProbeHelper& operator=(const KubernetesProbeHelper&) = delete;
    KubernetesProbeHelper(KubernetesProbeHelper&&) = delete;
    KubernetesProbeHelper& operator=(KubernetesProbeHelper&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::container
