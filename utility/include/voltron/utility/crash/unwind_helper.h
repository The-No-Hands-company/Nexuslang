#pragma once

#include <string>
#include <vector>

namespace voltron::utility::crash {

/**
 * @brief Manual stack unwinding for analysis
 * 
 * TODO: Implement comprehensive unwind_helper functionality
 */
class UnwindHelper {
public:
    static UnwindHelper& instance();

    /**
     * @brief Initialize unwind_helper
     */
    void initialize();

    /**
     * @brief Shutdown unwind_helper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    UnwindHelper() = default;
    ~UnwindHelper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::crash
