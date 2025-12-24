#pragma once

#include <string>
#include <vector>

namespace voltron::utility::reflection {

/**
 * @brief Iterate over struct members
 * 
 * TODO: Implement comprehensive member_iterator functionality
 */
class MemberIterator {
public:
    static MemberIterator& instance();

    /**
     * @brief Initialize member_iterator
     */
    void initialize();

    /**
     * @brief Shutdown member_iterator
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    MemberIterator() = default;
    ~MemberIterator() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::reflection
