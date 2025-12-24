#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::codegen {

/**
 * @brief Debug variadic template expansion
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Codegen
 * @version 1.0.0
 */
class VariadicExpanderHelper {
public:
    /**
     * @brief Get singleton instance
     */
    static VariadicExpanderHelper& instance();

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
    VariadicExpanderHelper() = default;
    ~VariadicExpanderHelper() = default;
    
    // Non-copyable, non-movable
    VariadicExpanderHelper(const VariadicExpanderHelper&) = delete;
    VariadicExpanderHelper& operator=(const VariadicExpanderHelper&) = delete;
    VariadicExpanderHelper(VariadicExpanderHelper&&) = delete;
    VariadicExpanderHelper& operator=(VariadicExpanderHelper&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::codegen
