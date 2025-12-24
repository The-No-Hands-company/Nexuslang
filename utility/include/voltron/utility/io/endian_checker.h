#pragma once

#include <string>
#include <vector>

namespace voltron::utility::io {

/**
 * @brief Endianness validation
 * 
 * TODO: Implement comprehensive endian_checker functionality
 */
class EndianChecker {
public:
    static EndianChecker& instance();

    /**
     * @brief Initialize endian_checker
     */
    void initialize();

    /**
     * @brief Shutdown endian_checker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    EndianChecker() = default;
    ~EndianChecker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::io
