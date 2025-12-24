#pragma once

#include <string>
#include <vector>

namespace voltron::utility::statemachine {

/**
 * @brief Generate GraphViz diagrams
 * 
 * TODO: Implement comprehensive fsm_dot_generator functionality
 */
class FsmDotGenerator {
public:
    static FsmDotGenerator& instance();

    /**
     * @brief Initialize fsm_dot_generator
     */
    void initialize();

    /**
     * @brief Shutdown fsm_dot_generator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    FsmDotGenerator() = default;
    ~FsmDotGenerator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::statemachine
