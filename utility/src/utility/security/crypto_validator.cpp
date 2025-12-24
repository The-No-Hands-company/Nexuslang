#include <voltron/utility/security/crypto_validator.h>
#include <iostream>

namespace voltron::utility::security {

CryptoValidator& CryptoValidator::instance() {
    static CryptoValidator instance;
    return instance;
}

void CryptoValidator::initialize() {
    enabled_ = true;
    std::cout << "[CryptoValidator] Initialized\n";
}

void CryptoValidator::shutdown() {
    enabled_ = false;
    std::cout << "[CryptoValidator] Shutdown\n";
}

bool CryptoValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::security
