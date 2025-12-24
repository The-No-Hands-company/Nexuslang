#pragma once

#include <string>
#include <vector>

namespace voltron::utility::database {

/**
 * @brief Debug ORM mappings
 * 
 * TODO: Implement comprehensive orm_debugger functionality
 */
class OrmDebugger {
public:
    static OrmDebugger& instance();

    /**
     * @brief Initialize orm_debugger
     */
    void initialize();

    /**
     * @brief Shutdown orm_debugger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    OrmDebugger() = default;
    ~OrmDebugger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::database
