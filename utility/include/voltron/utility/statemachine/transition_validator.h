#pragma once

#include <string>
#include <vector>

namespace voltron::utility::statemachine {

/**
 * @brief Validate legal transitions
 * 
 * TODO: Implement comprehensive transition_validator functionality
 */
class TransitionValidator {
public:
    static TransitionValidator& instance();

    /**
     * @brief Initialize transition_validator
     */
    void initialize();

    /**
     * @brief Shutdown transition_validator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TransitionValidator() = default;
    ~TransitionValidator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::statemachine
