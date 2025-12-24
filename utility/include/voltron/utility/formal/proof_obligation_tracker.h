#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::formal {

/**
 * @brief Track formal proof obligations
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Formal
 * @version 1.0.0
 */
class ProofObligationTracker {
public:
    /**
     * @brief Get singleton instance
     */
    static ProofObligationTracker& instance();

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
    ProofObligationTracker() = default;
    ~ProofObligationTracker() = default;
    
    // Non-copyable, non-movable
    ProofObligationTracker(const ProofObligationTracker&) = delete;
    ProofObligationTracker& operator=(const ProofObligationTracker&) = delete;
    ProofObligationTracker(ProofObligationTracker&&) = delete;
    ProofObligationTracker& operator=(ProofObligationTracker&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::formal
