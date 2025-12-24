#pragma once

#include <string>
#include <vector>

namespace voltron::utility::testing {

/**
 * @brief Base class for test fixtures
 * 
 * TODO: Implement comprehensive test_fixture_base functionality
 */
class TestFixtureBase {
public:
    static TestFixtureBase& instance();

    /**
     * @brief Initialize test_fixture_base
     */
    void initialize();

    /**
     * @brief Shutdown test_fixture_base
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TestFixtureBase() = default;
    ~TestFixtureBase() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::testing
