#pragma once

#include <string>
#include <vector>

namespace voltron::utility::cpp23 {

/**
 * @brief Detect abandoned coroutines
 * 
 * TODO: Implement comprehensive coroutine_leak_detector functionality
 */
class CoroutineLeakDetector {
public:
    static CoroutineLeakDetector& instance();

    /**
     * @brief Initialize coroutine_leak_detector
     */
    void initialize();

    /**
     * @brief Shutdown coroutine_leak_detector
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CoroutineLeakDetector() = default;
    ~CoroutineLeakDetector() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::cpp23
