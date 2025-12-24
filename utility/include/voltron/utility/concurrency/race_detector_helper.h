#pragma once

#include <string>
#include <vector>

namespace voltron::utility::concurrency {

/**
 * @brief ThreadSanitizer integration
 * 
 * TODO: Implement comprehensive race_detector_helper functionality
 */
class RaceDetectorHelper {
public:
    static RaceDetectorHelper& instance();

    /**
     * @brief Initialize race_detector_helper
     */
    void initialize();

    /**
     * @brief Shutdown race_detector_helper
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    RaceDetectorHelper() = default;
    ~RaceDetectorHelper() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::concurrency
