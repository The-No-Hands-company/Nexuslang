#pragma once

#include <string>
#include <vector>

namespace voltron::utility::testing {

/**
 * @brief Generate test data
 * 
 * TODO: Implement comprehensive test_data_generator functionality
 */
class TestDataGenerator {
public:
    static TestDataGenerator& instance();

    /**
     * @brief Initialize test_data_generator
     */
    void initialize();

    /**
     * @brief Shutdown test_data_generator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TestDataGenerator() = default;
    ~TestDataGenerator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::testing
