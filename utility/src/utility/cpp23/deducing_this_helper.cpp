#include <voltron/utility/cpp23/deducing_this_helper.h>
#include <iostream>

namespace voltron::utility::cpp23 {

DeducingThisHelper& DeducingThisHelper::instance() {
    static DeducingThisHelper instance;
    return instance;
}

void DeducingThisHelper::initialize() {
    enabled_ = true;
    std::cout << "[DeducingThisHelper] Initialized\n";
}

void DeducingThisHelper::shutdown() {
    enabled_ = false;
    std::cout << "[DeducingThisHelper] Shutdown\n";
}

bool DeducingThisHelper::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
