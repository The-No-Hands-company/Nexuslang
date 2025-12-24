#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Test RNG quality
 */
class RandomQualityTester {
public:
    static RandomQualityTester& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    RandomQualityTester() = default;
    ~RandomQualityTester() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
