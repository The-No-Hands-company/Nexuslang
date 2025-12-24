#include <voltron/utility/datastructures/tree_validator.h>
#include <iostream>

namespace voltron::utility::datastructures {

TreeValidator& TreeValidator::instance() {
    static TreeValidator instance;
    return instance;
}

void TreeValidator::initialize() {
    enabled_ = true;
    std::cout << "[TreeValidator] Initialized\n";
}

void TreeValidator::shutdown() {
    enabled_ = false;
    std::cout << "[TreeValidator] Shutdown\n";
}

bool TreeValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::datastructures
