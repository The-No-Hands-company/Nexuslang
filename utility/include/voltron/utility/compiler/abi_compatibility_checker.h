#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Detect ABI breaks
 * 
 * TODO: Implement comprehensive abi_compatibility_checker functionality
 */
class AbiCompatibilityChecker {
public:
    static AbiCompatibilityChecker& instance();

    /**
     * @brief Initialize abi_compatibility_checker
     */
    void initialize();

    /**
     * @brief Shutdown abi_compatibility_checker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    AbiCompatibilityChecker() = default;
    ~AbiCompatibilityChecker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
