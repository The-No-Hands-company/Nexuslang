#include <voltron/utility/network/dns_resolver_debug.h>
#include <iostream>

namespace voltron::utility::network {

DnsResolverDebug& DnsResolverDebug::instance() {
    static DnsResolverDebug instance;
    return instance;
}

void DnsResolverDebug::initialize() {
    enabled_ = true;
    std::cout << "[DnsResolverDebug] Initialized\n";
}

void DnsResolverDebug::shutdown() {
    enabled_ = false;
    std::cout << "[DnsResolverDebug] Shutdown\n";
}

bool DnsResolverDebug::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
