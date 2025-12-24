#include <voltron/utility/types/alignment_checker.h>
#include <iostream>

namespace voltron::utility::types {

AlignmentChecker& AlignmentChecker::instance() {
    static AlignmentChecker instance;
    return instance;
}

void AlignmentChecker::initialize() {
    enabled_ = true;
    std::cout << "[AlignmentChecker] Initialized\n";
}

void AlignmentChecker::shutdown() {
    enabled_ = false;
    std::cout << "[AlignmentChecker] Shutdown\n";
}

bool AlignmentChecker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::types
