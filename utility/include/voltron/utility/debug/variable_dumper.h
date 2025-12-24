#pragma once

#include <string>
#include <vector>

namespace voltron::utility::debug {

/**
 * @brief Dump variable states
 * 
 * TODO: Implement comprehensive variable_dumper functionality
 */
class VariableDumper {
public:
    static VariableDumper& instance();

    /**
     * @brief Initialize variable_dumper
     */
    void initialize();

    /**
     * @brief Shutdown variable_dumper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    VariableDumper() = default;
    ~VariableDumper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::debug
