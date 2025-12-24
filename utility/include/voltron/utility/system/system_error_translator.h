#pragma once

#include <string>
#include <vector>

namespace voltron::utility::system {

/**
 * @brief Convert system errors to messages
 * 
 * TODO: Implement comprehensive system_error_translator functionality
 */
class SystemErrorTranslator {
public:
    static SystemErrorTranslator& instance();

    /**
     * @brief Initialize system_error_translator
     */
    void initialize();

    /**
     * @brief Shutdown system_error_translator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    SystemErrorTranslator() = default;
    ~SystemErrorTranslator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::system
