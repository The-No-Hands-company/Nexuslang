#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::codegen {

/**
 * @brief Debug generated code outputs
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Codegen
 * @version 1.0.0
 */
class CodeGeneratorDebugger {
public:
    /**
     * @brief Get singleton instance
     */
    static CodeGeneratorDebugger& instance();

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
    CodeGeneratorDebugger() = default;
    ~CodeGeneratorDebugger() = default;
    
    // Non-copyable, non-movable
    CodeGeneratorDebugger(const CodeGeneratorDebugger&) = delete;
    CodeGeneratorDebugger& operator=(const CodeGeneratorDebugger&) = delete;
    CodeGeneratorDebugger(CodeGeneratorDebugger&&) = delete;
    CodeGeneratorDebugger& operator=(CodeGeneratorDebugger&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::codegen
