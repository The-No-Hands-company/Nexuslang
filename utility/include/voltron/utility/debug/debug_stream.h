#pragma once

#include <string>
#include <vector>

namespace voltron::utility::debug {

/**
 * @brief Debug-only output streams
 * 
 * TODO: Implement comprehensive debug_stream functionality
 */
class DebugStream {
public:
    static DebugStream& instance();

    /**
     * @brief Initialize debug_stream
     */
    void initialize();

    /**
     * @brief Shutdown debug_stream
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DebugStream() = default;
    ~DebugStream() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::debug
