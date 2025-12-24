#include <voltron/utility/datastructures/iterator_debug.h>
#include <iostream>

namespace voltron::utility::datastructures {

IteratorDebug& IteratorDebug::instance() {
    static IteratorDebug instance;
    return instance;
}

void IteratorDebug::initialize() {
    enabled_ = true;
    std::cout << "[IteratorDebug] Initialized\n";
}

void IteratorDebug::shutdown() {
    enabled_ = false;
    std::cout << "[IteratorDebug] Shutdown\n";
}

bool IteratorDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::datastructures
