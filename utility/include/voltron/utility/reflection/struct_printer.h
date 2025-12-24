#pragma once

#include <string>
#include <vector>

namespace voltron::utility::reflection {

/**
 * @brief Auto-print struct contents
 * 
 * TODO: Implement comprehensive struct_printer functionality
 */
class StructPrinter {
public:
    static StructPrinter& instance();

    /**
     * @brief Initialize struct_printer
     */
    void initialize();

    /**
     * @brief Shutdown struct_printer
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    StructPrinter() = default;
    ~StructPrinter() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::reflection
