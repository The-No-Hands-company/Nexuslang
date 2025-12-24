#include <voltron/utility/network/network_error_classifier.h>
#include <iostream>

namespace voltron::utility::network {

NetworkErrorClassifier& NetworkErrorClassifier::instance() {
    static NetworkErrorClassifier instance;
    return instance;
}

void NetworkErrorClassifier::initialize() {
    enabled_ = true;
    std::cout << "[NetworkErrorClassifier] Initialized\n";
}

void NetworkErrorClassifier::shutdown() {
    enabled_ = false;
    std::cout << "[NetworkErrorClassifier] Shutdown\n";
}

bool NetworkErrorClassifier::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::network
