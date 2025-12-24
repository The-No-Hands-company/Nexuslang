#include <voltron/utility/graphics/shader_compiler_error_parser.h>
#include <iostream>

namespace voltron::utility::graphics {

ShaderCompilerErrorParser& ShaderCompilerErrorParser::instance() {
    static ShaderCompilerErrorParser instance;
    return instance;
}

void ShaderCompilerErrorParser::initialize() {
    enabled_ = true;
    std::cout << "[ShaderCompilerErrorParser] Initialized\n";
}

void ShaderCompilerErrorParser::shutdown() {
    enabled_ = false;
    std::cout << "[ShaderCompilerErrorParser] Shutdown\n";
}

bool ShaderCompilerErrorParser::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::graphics
