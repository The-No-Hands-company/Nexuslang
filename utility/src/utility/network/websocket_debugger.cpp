#include <voltron/utility/network/websocket_debugger.h>
#include <iostream>

namespace voltron::utility::network {

WebsocketDebugger& WebsocketDebugger::instance() {
    static WebsocketDebugger instance;
    return instance;
}

void WebsocketDebugger::initialize() {
    enabled_ = true;
    std::cout << "[WebsocketDebugger] Initialized\n";
}

void WebsocketDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[WebsocketDebugger] Shutdown\n";
}

bool WebsocketDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
