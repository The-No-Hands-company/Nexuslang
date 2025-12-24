#pragma once

#include <string>
#include <vector>

namespace voltron::utility::testing {

/**
 * @brief Helper macros for mocks
 * 
 * TODO: Implement comprehensive mock_generator functionality
 */
class MockGenerator {
public:
    static MockGenerator& instance();

    /**
     * @brief Initialize mock_generator
     */
    void initialize();

    /**
     * @brief Shutdown mock_generator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MockGenerator() = default;
    ~MockGenerator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::testing
