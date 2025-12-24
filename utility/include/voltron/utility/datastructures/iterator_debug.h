#pragma once

#include <string>
#include <vector>

namespace voltron::utility::datastructures {

/**
 * @brief Check iterator validity
 * 
 * TODO: Implement comprehensive iterator_debug functionality
 */
class IteratorDebug {
public:
    static IteratorDebug& instance();

    /**
     * @brief Initialize iterator_debug
     */
    void initialize();

    /**
     * @brief Shutdown iterator_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    IteratorDebug() = default;
    ~IteratorDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::datastructures
