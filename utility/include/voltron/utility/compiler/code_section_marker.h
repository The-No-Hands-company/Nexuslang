#pragma once

#include <string>
#include <vector>

namespace voltron::utility::compiler {

/**
 * @brief Mark hot/cold code sections
 * 
 * TODO: Implement comprehensive code_section_marker functionality
 */
class CodeSectionMarker {
public:
    static CodeSectionMarker& instance();

    /**
     * @brief Initialize code_section_marker
     */
    void initialize();

    /**
     * @brief Shutdown code_section_marker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    CodeSectionMarker() = default;
    ~CodeSectionMarker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::compiler
