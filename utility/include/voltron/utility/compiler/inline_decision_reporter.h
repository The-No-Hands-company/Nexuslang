#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Report inlining decisions
 * 
 * TODO: Implement comprehensive inline_decision_reporter functionality
 */
class InlineDecisionReporter {
public:
    static InlineDecisionReporter& instance();

    /**
     * @brief Initialize inline_decision_reporter
     */
    void initialize();

    /**
     * @brief Shutdown inline_decision_reporter
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    InlineDecisionReporter() = default;
    ~InlineDecisionReporter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
