#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::parser {

/**
 * @brief Dump symbol table contents
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Parser
 * @version 1.0.0
 */
class SymbolTableDumper {
public:
    /**
     * @brief Get singleton instance
     */
    static SymbolTableDumper& instance();

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
    SymbolTableDumper() = default;
    ~SymbolTableDumper() = default;
    
    // Non-copyable, non-movable
    SymbolTableDumper(const SymbolTableDumper&) = delete;
    SymbolTableDumper& operator=(const SymbolTableDumper&) = delete;
    SymbolTableDumper(SymbolTableDumper&&) = delete;
    SymbolTableDumper& operator=(SymbolTableDumper&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::parser
