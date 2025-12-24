#pragma once

#include <string>
#include <vector>

namespace voltron::utility::database {

/**
 * @brief Track DB transaction boundaries
 * 
 * TODO: Implement comprehensive transaction_tracker functionality
 */
class TransactionTracker {
public:
    static TransactionTracker& instance();

    /**
     * @brief Initialize transaction_tracker
     */
    void initialize();

    /**
     * @brief Shutdown transaction_tracker
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    TransactionTracker() = default;
    ~TransactionTracker() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::database
