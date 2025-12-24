#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Dump graphics pipeline state
 * 
 * TODO: Implement comprehensive pipeline_state_dumper functionality
 */
class PipelineStateDumper {
public:
    static PipelineStateDumper& instance();

    /**
     * @brief Initialize pipeline_state_dumper
     */
    void initialize();

    /**
     * @brief Shutdown pipeline_state_dumper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    PipelineStateDumper() = default;
    ~PipelineStateDumper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
