#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Debug complex macros
 * 
 * TODO: Implement comprehensive macro_expansion_debugger functionality
 */
class MacroExpansionDebugger {
public:
    static MacroExpansionDebugger& instance();

    /**
     * @brief Initialize macro_expansion_debugger
     */
    void initialize();

    /**
     * @brief Shutdown macro_expansion_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MacroExpansionDebugger() = default;
    ~MacroExpansionDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
