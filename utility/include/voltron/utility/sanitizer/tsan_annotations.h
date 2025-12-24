#pragma once

#include <string>
#include <vector>

namespace voltron::utility::sanitizer {

/**
 * @brief ThreadSanitizer annotations
 * 
 * TODO: Implement comprehensive tsan_annotations functionality
 */
class TsanAnnotations {
public:
    static TsanAnnotations& instance();

    /**
     * @brief Initialize tsan_annotations
     */
    void initialize();

    /**
     * @brief Shutdown tsan_annotations
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TsanAnnotations() = default;
    ~TsanAnnotations() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::sanitizer
