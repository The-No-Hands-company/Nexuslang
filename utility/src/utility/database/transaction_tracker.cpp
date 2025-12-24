#include <voltron/utility/database/transaction_tracker.h>
#include <iostream>

namespace voltron::utility::database {

TransactionTracker& TransactionTracker::instance() {
    static TransactionTracker instance;
    return instance;
}

void TransactionTracker::initialize() {
    enabled_ = true;
    std::cout << "[TransactionTracker] Initialized\n";
}

void TransactionTracker::shutdown() {
    enabled_ = false;
    std::cout << "[TransactionTracker] Shutdown\n";
}

bool TransactionTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
