#include <voltron/utility/config/shutdown_handler.h>
#include <iostream>

namespace voltron::utility::config {

ShutdownHandler& ShutdownHandler::instance() {
    static ShutdownHandler instance;
    return instance;
}

void ShutdownHandler::initialize() {
    enabled_ = true;
    std::cout << "[ShutdownHandler] Initialized\n";
}

void ShutdownHandler::shutdown() {
    enabled_ = false;
    std::cout << "[ShutdownHandler] Shutdown\n";
}

bool ShutdownHandler::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
