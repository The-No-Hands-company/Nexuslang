#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::reversing {

/**
 * @brief Runtime disassembly utilities
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Reversing
 * @version 1.0.0
 */
class DisassemblerHelper {
public:
    /**
     * @brief Get singleton instance
     */
    static DisassemblerHelper& instance();

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
    DisassemblerHelper() = default;
    ~DisassemblerHelper() = default;
    
    // Non-copyable, non-movable
    DisassemblerHelper(const DisassemblerHelper&) = delete;
    DisassemblerHelper& operator=(const DisassemblerHelper&) = delete;
    DisassemblerHelper(DisassemblerHelper&&) = delete;
    DisassemblerHelper& operator=(DisassemblerHelper&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::reversing
