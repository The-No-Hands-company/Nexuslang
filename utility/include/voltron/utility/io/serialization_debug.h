#pragma once

#include <string>
#include <vector>

namespace voltron::utility::io {

/**
 * @brief Track serialization
 * 
 * TODO: Implement comprehensive serialization_debug functionality
 */
class SerializationDebug {
public:
    static SerializationDebug& instance();

    /**
     * @brief Initialize serialization_debug
     */
    void initialize();

    /**
     * @brief Shutdown serialization_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SerializationDebug() = default;
    ~SerializationDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::io
