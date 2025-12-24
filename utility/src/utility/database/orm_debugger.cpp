#include <voltron/utility/database/orm_debugger.h>
#include <iostream>

namespace voltron::utility::database {

OrmDebugger& OrmDebugger::instance() {
    static OrmDebugger instance;
    return instance;
}

void OrmDebugger::initialize() {
    enabled_ = true;
    std::cout << "[OrmDebugger] Initialized\n";
}

void OrmDebugger::shutdown() {
    enabled_ = false;
    std::cout << "[OrmDebugger] Shutdown\n";
}

bool OrmDebugger::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
