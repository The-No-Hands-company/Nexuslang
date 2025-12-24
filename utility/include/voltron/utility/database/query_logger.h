#pragma once

#include <string>
#include <vector>

namespace voltron::utility::database {

/**
 * @brief Log all SQL queries with timing
 * 
 * TODO: Implement comprehensive query_logger functionality
 */
class QueryLogger {
public:
    static QueryLogger& instance();

    /**
     * @brief Initialize query_logger
     */
    void initialize();

    /**
     * @brief Shutdown query_logger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    QueryLogger() = default;
    ~QueryLogger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::database
