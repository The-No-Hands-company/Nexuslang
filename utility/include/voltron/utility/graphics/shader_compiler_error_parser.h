#pragma once

#include <string>
#include <vector>

namespace voltron::utility::graphics {

/**
 * @brief Parse shader errors
 * 
 * TODO: Implement comprehensive shader_compiler_error_parser functionality
 */
class ShaderCompilerErrorParser {
public:
    static ShaderCompilerErrorParser& instance();

    /**
     * @brief Initialize shader_compiler_error_parser
     */
    void initialize();

    /**
     * @brief Shutdown shader_compiler_error_parser
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    ShaderCompilerErrorParser() = default;
    ~ShaderCompilerErrorParser() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::graphics
