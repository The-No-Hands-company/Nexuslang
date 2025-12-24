#pragma once

#include <string>
#include <vector>

namespace voltron::utility::debug {

/**
 * @brief Runtime disassembly inspection
 * 
 * TODO: Implement comprehensive disassembly_helper functionality
 */
class DisassemblyHelper {
public:
    static DisassemblyHelper& instance();

    /**
     * @brief Initialize disassembly_helper
     */
    void initialize();

    /**
     * @brief Shutdown disassembly_helper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DisassemblyHelper() = default;
    ~DisassemblyHelper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::debug
