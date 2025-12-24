#include <voltron/utility/reflection/member_iterator.h>
#include <iostream>

namespace voltron::utility::reflection {

MemberIterator& MemberIterator::instance() {
    static MemberIterator instance;
    return instance;
}

void MemberIterator::initialize() {
    enabled_ = true;
    std::cout << "[MemberIterator] Initialized\n";
}

void MemberIterator::shutdown() {
    enabled_ = false;
    std::cout << "[MemberIterator] Shutdown\n";
}

bool MemberIterator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::reflection
