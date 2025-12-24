#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief DNS resolution tracking
 * 
 * TODO: Implement comprehensive dns_resolver_debug functionality
 */
class DnsResolverDebug {
public:
    static DnsResolverDebug& instance();

    /**
     * @brief Initialize dns_resolver_debug
     */
    void initialize();

    /**
     * @brief Shutdown dns_resolver_debug
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    DnsResolverDebug() = default;
    ~DnsResolverDebug() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
