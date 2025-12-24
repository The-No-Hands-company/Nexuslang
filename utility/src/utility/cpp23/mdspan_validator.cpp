#include <voltron/utility/cpp23/mdspan_validator.h>
#include <iostream>

namespace voltron::utility::cpp23 {

MdspanValidator& MdspanValidator::instance() {
    static MdspanValidator instance;
    return instance;
}

void MdspanValidator::initialize() {
    enabled_ = true;
    std::cout << "[MdspanValidator] Initialized\n";
}

void MdspanValidator::shutdown() {
    enabled_ = false;
    std::cout << "[MdspanValidator] Shutdown\n";
}

bool MdspanValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::cpp23
