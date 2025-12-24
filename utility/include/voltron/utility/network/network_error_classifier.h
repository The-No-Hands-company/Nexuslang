#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief Categorize network errors
 * 
 * TODO: Implement comprehensive network_error_classifier functionality
 */
class NetworkErrorClassifier {
public:
    static NetworkErrorClassifier& instance();

    /**
     * @brief Initialize network_error_classifier
     */
    void initialize();

    /**
     * @brief Shutdown network_error_classifier
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    NetworkErrorClassifier() = default;
    ~NetworkErrorClassifier() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
