#pragma once

#include <string>
#include <vector>

namespace voltron::utility::crash {

/**
 * @brief Ensure proper core dump generation
 * 
 * TODO: Implement comprehensive core_dump_helper functionality
 */
class CoreDumpHelper {
public:
    static CoreDumpHelper& instance();

    /**
     * @brief Initialize core_dump_helper
     */
    void initialize();

    /**
     * @brief Shutdown core_dump_helper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CoreDumpHelper() = default;
    ~CoreDumpHelper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::crash
