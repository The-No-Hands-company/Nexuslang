#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::parser {

/**
 * @brief Visualize register allocation
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Parser
 * @version 1.0.0
 */
class RegisterAllocatorVisualizer {
public:
    /**
     * @brief Get singleton instance
     */
    static RegisterAllocatorVisualizer& instance();

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
    RegisterAllocatorVisualizer() = default;
    ~RegisterAllocatorVisualizer() = default;
    
    // Non-copyable, non-movable
    RegisterAllocatorVisualizer(const RegisterAllocatorVisualizer&) = delete;
    RegisterAllocatorVisualizer& operator=(const RegisterAllocatorVisualizer&) = delete;
    RegisterAllocatorVisualizer(RegisterAllocatorVisualizer&&) = delete;
    RegisterAllocatorVisualizer& operator=(RegisterAllocatorVisualizer&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::parser
