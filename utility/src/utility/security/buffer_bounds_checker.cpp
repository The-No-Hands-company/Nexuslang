#include "voltron/utility/security/buffer_bounds_checker.h"
#include <regex>
#include <filesystem>
#include <cstring>

namespace voltron::utility::security {

void BufferBoundsChecker::checkBounds(const void* buffer, size_t buffer_size,
                                     size_t offset, size_t access_size) {
    if (offset + access_size > buffer_size) {
        throw std::out_of_range("Buffer access out of bounds");
    }
}

void BufferBoundsChecker::checkedMemcpy(void* dest, size_t dest_size,
                                       const void* src, size_t src_size) {
    if (src_size > dest_size) {
        throw std::out_of_range("Source larger than destination buffer");
    }
    std::memcpy(dest, src, src_size);
}

void BufferBoundsChecker::checkedStrcpy(char* dest, size_t dest_size, const char* src) {
    size_t src_len = std::strlen(src);
    if (src_len >= dest_size) {
        throw std::out_of_range("String too long for destination buffer");
    }
    std::strcpy(dest, src);
}

bool PathTraversalValidator::isPathSafe(const std::string& path) {
    // Check for common traversal patterns
    if (path.find("..") != std::string::npos) return false;
    if (path.find("//") != std::string::npos) return false;
    if (path.find("\\\\") != std::string::npos) return false;
    return true;
}

std::string PathTraversalValidator::sanitizePath(const std::string& path) {
    namespace fs = std::filesystem;
    try {
        auto canonical = fs::weakly_canonical(path);
        return canonical.string();
    } catch (...) {
        throw std::runtime_error("Invalid path");
    }
}

bool PathTraversalValidator::isWithinBaseDir(const std::string& path,
                                            const std::string& base_dir) {
    namespace fs = std::filesystem;
    auto canonical_path = fs::weakly_canonical(path);
    auto canonical_base = fs::weakly_canonical(base_dir);

    auto rel = fs::relative(canonical_path, canonical_base);
    return !rel.string().starts_with("..");
}

// Simple implementation - in production use proper secret management
static std::vector<std::pair<std::string, std::regex>> secret_patterns;

void SecretLeakDetector::registerSecretPattern(const std::string& pattern_name,
                                              const std::string& regex_str) {
    secret_patterns.emplace_back(pattern_name, std::regex(regex_str));
}

bool SecretLeakDetector::containsSecrets(const std::string& text) {
    for (const auto& [name, pattern] : secret_patterns) {
        if (std::regex_search(text, pattern)) {
            return true;
        }
    }
    return false;
}

std::string SecretLeakDetector::redactSecrets(const std::string& text) {
    std::string result = text;
    for (const auto& [name, pattern] : secret_patterns) {
        result = std::regex_replace(result, pattern, "[REDACTED:" + name + "]");
    }
    return result;
}

void SecureWipe::wipe(void* ptr, size_t size) {
    // Use volatile to prevent optimization
    volatile unsigned char* p = static_cast<volatile unsigned char*>(ptr);
    while (size--) {
        *p++ = 0;
    }
}

} // namespace voltron::utility::security
