#pragma once

#include <string>
#include <vector>

namespace voltron::utility::security {

/**
 * @brief Validate crypto usage
 * 
 * TODO: Implement comprehensive crypto_validator functionality
 */
class CryptoValidator {
public:
    static CryptoValidator& instance();

    /**
     * @brief Initialize crypto_validator
     */
    void initialize();

    /**
     * @brief Shutdown crypto_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CryptoValidator() = default;
    ~CryptoValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::security
