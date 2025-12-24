#pragma once

#include <string>
#include <vector>

namespace voltron::utility::sanitizer {

/**
 * @brief Coverage-guided fuzzing
 * 
 * TODO: Implement comprehensive sanitizer_coverage functionality
 */
class SanitizerCoverage {
public:
    static SanitizerCoverage& instance();

    /**
     * @brief Initialize sanitizer_coverage
     */
    void initialize();

    /**
     * @brief Shutdown sanitizer_coverage
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SanitizerCoverage() = default;
    ~SanitizerCoverage() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::sanitizer
