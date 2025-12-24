#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Measure compilation overhead
 * 
 * TODO: Implement comprehensive compile_time_counter functionality
 */
class CompileTimeCounter {
public:
    static CompileTimeCounter& instance();

    /**
     * @brief Initialize compile_time_counter
     */
    void initialize();

    /**
     * @brief Shutdown compile_time_counter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CompileTimeCounter() = default;
    ~CompileTimeCounter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
