#include <voltron/utility/system/privilege_checker.h>
#include <iostream>

namespace voltron::utility::system {

PrivilegeChecker& PrivilegeChecker::instance() {
    static PrivilegeChecker instance;
    return instance;
}

void PrivilegeChecker::initialize() {
    enabled_ = true;
    std::cout << "[PrivilegeChecker] Initialized\n";
}

void PrivilegeChecker::shutdown() {
    enabled_ = false;
    std::cout << "[PrivilegeChecker] Shutdown\n";
}

bool PrivilegeChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::system
