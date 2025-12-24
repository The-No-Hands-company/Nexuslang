#pragma once

#include <string>
#include <vector>

namespace voltron::utility::plugin {

/**
 * @brief Debug symbol resolution
 */
class SymbolResolverDebug {
public:
    static SymbolResolverDebug& instance();
    void initialize();
    void shutdown();
    bool isEnabled() const;

private:
    SymbolResolverDebug() = default;
    ~SymbolResolverDebug() = default;
    bool enabled_ = false;
};

} // namespace voltron::utility::plugin
