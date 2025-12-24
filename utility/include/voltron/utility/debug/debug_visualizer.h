#pragma once

#include <string>
#include <vector>

namespace voltron::utility::debug {

/**
 * @brief Pretty-printers for GDB/LLDB
 * 
 * TODO: Implement comprehensive debug_visualizer functionality
 */
class DebugVisualizer {
public:
    static DebugVisualizer& instance();

    /**
     * @brief Initialize debug_visualizer
     */
    void initialize();

    /**
     * @brief Shutdown debug_visualizer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DebugVisualizer() = default;
    ~DebugVisualizer() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::debug
