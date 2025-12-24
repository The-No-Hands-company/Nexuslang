#pragma once

#include <string>
#include <vector>

namespace voltron::utility::reflection {

/**
 * @brief Bidirectional enum↔string
 * 
 * TODO: Implement comprehensive enum_to_string functionality
 */
class EnumToString {
public:
    static EnumToString& instance();

    /**
     * @brief Initialize enum_to_string
     */
    void initialize();

    /**
     * @brief Shutdown enum_to_string
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    EnumToString() = default;
    ~EnumToString() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::reflection
