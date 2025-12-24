#pragma once

#include <string>
#include <vector>

namespace voltron::utility::profiling {

/**
 * @brief Generate profiling data for visualization
 * 
 * TODO: Implement comprehensive flame_graph_generator functionality
 */
class FlameGraphGenerator {
public:
    static FlameGraphGenerator& instance();

    /**
     * @brief Initialize flame_graph_generator
     */
    void initialize();

    /**
     * @brief Shutdown flame_graph_generator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    FlameGraphGenerator() = default;
    ~FlameGraphGenerator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::profiling
