#include <voltron/utility/reflection/type_introspector.h>
#include <iostream>

namespace voltron::utility::reflection {

TypeIntrospector& TypeIntrospector::instance() {
    static TypeIntrospector instance;
    return instance;
}

void TypeIntrospector::initialize() {
    enabled_ = true;
    std::cout << "[TypeIntrospector] Initialized\n";
}

void TypeIntrospector::shutdown() {
    enabled_ = false;
    std::cout << "[TypeIntrospector] Shutdown\n";
}

bool TypeIntrospector::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
