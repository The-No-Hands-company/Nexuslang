#include "voltron/utility/graphics/opengl_error_checker.h"
#include <iostream>
#include <sstream>
#include <regex>

namespace voltron::utility::graphics {

// Note: This implementation assumes OpenGL headers are available
// In a real implementation, you'd include <GL/gl.h> or similar

bool OpenGLErrorChecker::checkErrors(const char* file, int line, const char* function) {
    // Placeholder - real implementation would call glGetError()
    // unsigned int error = glGetError();
    unsigned int error = 0; // GL_NO_ERROR

    if (error != 0) {
        std::cerr << "OpenGL Error: " << errorCodeToString(error)
                  << " at " << file << ":" << line << " in " << function << "\n";
        return false;
    }
    return true;
}

std::string OpenGLErrorChecker::errorCodeToString(unsigned int error_code) {
    switch (error_code) {
        case 0x0500: return "GL_INVALID_ENUM";
        case 0x0501: return "GL_INVALID_VALUE";
        case 0x0502: return "GL_INVALID_OPERATION";
        case 0x0503: return "GL_STACK_OVERFLOW";
        case 0x0504: return "GL_STACK_UNDERFLOW";
        case 0x0505: return "GL_OUT_OF_MEMORY";
        case 0x0506: return "GL_INVALID_FRAMEBUFFER_OPERATION";
        default: return "UNKNOWN_ERROR";
    }
}

bool FramebufferValidator::isComplete(unsigned int framebuffer_id) {
    // Placeholder - real implementation would call glCheckFramebufferStatus()
    return true;
}

std::string FramebufferValidator::getStatusMessage(unsigned int framebuffer_id) {
    // Placeholder - real implementation would interpret framebuffer status
    return "GL_FRAMEBUFFER_COMPLETE";
}

void GPUResourceTracker::recordAllocation(ResourceType type, unsigned int id,
                                         size_t size_bytes, const std::string& name) {
    std::lock_guard<std::mutex> lock(mutex_);
    resources_[id] = {type, id, size_bytes, name};
}

void GPUResourceTracker::recordDeallocation(ResourceType type, unsigned int id) {
    std::lock_guard<std::mutex> lock(mutex_);
    resources_.erase(id);
}

GPUResourceTracker::ResourceStats GPUResourceTracker::getStats(ResourceType type) const {
    std::lock_guard<std::mutex> lock(mutex_);

    ResourceStats stats;
    for (const auto& [id, info] : resources_) {
        if (info.type == type) {
            stats.count++;
            stats.total_bytes += info.size_bytes;
        }
    }
    return stats;
}

void GPUResourceTracker::printReport(std::ostream& os) const {
    std::lock_guard<std::mutex> lock(mutex_);

    os << "\n=== GPU Resource Tracker Report ===\n";

    const char* type_names[] = {
        "Texture", "Buffer", "Shader", "Program",
        "Framebuffer", "Renderbuffer", "VertexArray"
    };

    for (int i = 0; i < 7; ++i) {
        auto type = static_cast<ResourceType>(i);
        auto stats = getStats(type);
        if (stats.count > 0) {
            os << type_names[i] << "s: " << stats.count
               << " (" << stats.total_bytes << " bytes)\n";
        }
    }

    os << "====================================\n";
}

std::vector<std::pair<GPUResourceTracker::ResourceType, unsigned int>>
GPUResourceTracker::detectLeaks() const {
    std::lock_guard<std::mutex> lock(mutex_);

    std::vector<std::pair<ResourceType, unsigned int>> leaks;
    for (const auto& [id, info] : resources_) {
        leaks.emplace_back(info.type, id);
    }
    return leaks;
}

std::vector<ShaderCompilerErrorParser::ShaderError>
ShaderCompilerErrorParser::parseErrorLog(const std::string& log,
                                        const std::string& source_code) {
    std::vector<ShaderError> errors;

    // Parse common shader error formats
    // NVIDIA: "0(line) : error C1234: message"
    // AMD: "ERROR: 0:line: message"
    std::regex nvidia_pattern(R"((\d+)\((\d+)\)\s*:\s*error\s+\w+:\s*(.+))");
    std::regex amd_pattern(R"(ERROR:\s*\d+:(\d+):\s*(.+))");

    std::istringstream iss(log);
    std::string line;
    while (std::getline(iss, line)) {
        std::smatch match;

        if (std::regex_search(line, match, nvidia_pattern)) {
            ShaderError error;
            error.line_number = std::stoi(match[2]);
            error.error_message = match[3];
            errors.push_back(error);
        } else if (std::regex_search(line, match, amd_pattern)) {
            ShaderError error;
            error.line_number = std::stoi(match[1]);
            error.error_message = match[2];
            errors.push_back(error);
        }
    }

    return errors;
}

void ShaderCompilerErrorParser::printErrors(const std::vector<ShaderError>& errors,
                                           std::ostream& os) {
    os << "\n=== Shader Compilation Errors ===\n";
    for (const auto& error : errors) {
        os << "Line " << error.line_number << ": " << error.error_message << "\n";
        if (!error.source_line.empty()) {
            os << "  > " << error.source_line << "\n";
        }
    }
    os << "==================================\n";
}

void PipelineStateDumper::dumpState(std::ostream& os) {
    os << "\n=== OpenGL Pipeline State ===\n";
    dumpBlendState(os);
    dumpDepthState(os);
    dumpStencilState(os);
    dumpRasterizerState(os);
    os << "=============================\n";
}

void PipelineStateDumper::dumpBlendState(std::ostream& os) {
    os << "Blend State:\n";
    // Placeholder - real implementation would query OpenGL state
    os << "  Enabled: [query GL_BLEND]\n";
    os << "  Func: [query glGetIntegerv(GL_BLEND_SRC_RGB, ...)]\n";
}

void PipelineStateDumper::dumpDepthState(std::ostream& os) {
    os << "Depth State:\n";
    os << "  Test Enabled: [query GL_DEPTH_TEST]\n";
    os << "  Write Enabled: [query GL_DEPTH_WRITEMASK]\n";
}

void PipelineStateDumper::dumpStencilState(std::ostream& os) {
    os << "Stencil State:\n";
    os << "  Test Enabled: [query GL_STENCIL_TEST]\n";
}

void PipelineStateDumper::dumpRasterizerState(std::ostream& os) {
    os << "Rasterizer State:\n";
    os << "  Cull Face: [query GL_CULL_FACE]\n";
    os << "  Polygon Mode: [query GL_POLYGON_MODE]\n";
}

} // namespace voltron::utility::graphics
