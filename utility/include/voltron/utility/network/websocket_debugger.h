#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief WebSocket debugging
 * 
 * TODO: Implement comprehensive websocket_debugger functionality
 */
class WebsocketDebugger {
public:
    static WebsocketDebugger& instance();

    /**
     * @brief Initialize websocket_debugger
     */
    void initialize();

    /**
     * @brief Shutdown websocket_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    WebsocketDebugger() = default;
    ~WebsocketDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
