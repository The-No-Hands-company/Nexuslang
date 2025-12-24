#include <voltron/utility/security/path_traversal_validator.h>
#include <iostream>

namespace voltron::utility::security {

PathTraversalValidator& PathTraversalValidator::instance() {
    static PathTraversalValidator instance;
    return instance;
}

void PathTraversalValidator::initialize() {
    enabled_ = true;
    std::cout << "[PathTraversalValidator] Initialized\n";
}

void PathTraversalValidator::shutdown() {
    enabled_ = false;
    std::cout << "[PathTraversalValidator] Shutdown\n";
}

bool PathTraversalValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
