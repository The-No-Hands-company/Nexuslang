#include <voltron/utility/database/cache_coherence_validator.h>
#include <iostream>

namespace voltron::utility::database {

CacheCoherenceValidator& CacheCoherenceValidator::instance() {
    static CacheCoherenceValidator instance;
    return instance;
}

void CacheCoherenceValidator::initialize() {
    enabled_ = true;
    std::cout << "[CacheCoherenceValidator] Initialized\n";
}

void CacheCoherenceValidator::shutdown() {
    enabled_ = false;
    std::cout << "[CacheCoherenceValidator] Shutdown\n";
}

bool CacheCoherenceValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
