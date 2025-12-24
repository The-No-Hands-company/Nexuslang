#include <voltron/utility/security/privilege_escalation_guard.h>
#include <iostream>

namespace voltron::utility::security {

PrivilegeEscalationGuard& PrivilegeEscalationGuard::instance() {
    static PrivilegeEscalationGuard instance;
    return instance;
}

void PrivilegeEscalationGuard::initialize() {
    enabled_ = true;
    std::cout << "[PrivilegeEscalationGuard] Initialized\n";
}

void PrivilegeEscalationGuard::shutdown() {
    enabled_ = false;
    std::cout << "[PrivilegeEscalationGuard] Shutdown\n";
}

bool PrivilegeEscalationGuard::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
