#pragma once

#include <string>
#include <vector>

namespace voltron::utility::algorithmic {

/**
 * @brief Analyze hash distribution
 */
class HashQualityAnalyzer {
public:
    static HashQualityAnalyzer& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    HashQualityAnalyzer() = default;
    ~HashQualityAnalyzer() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::algorithmic
