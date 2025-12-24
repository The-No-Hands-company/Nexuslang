#pragma once

#include <string>
#include <vector>

namespace voltron::utility::reflection {

/**
 * @brief Runtime type information
 * 
 * TODO: Implement comprehensive type_introspector functionality
 */
class TypeIntrospector {
public:
    static TypeIntrospector& instance();

    /**
     * @brief Initialize type_introspector
     */
    void initialize();

    /**
     * @brief Shutdown type_introspector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TypeIntrospector() = default;
    ~TypeIntrospector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::reflection
