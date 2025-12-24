#pragma once

#include <source_location>

namespace voltron::utility::assertions {

/// @brief Function precondition validator (Design by Contract)
class Precondition {
public:
    static void check(bool condition, const char* message,
                     std::source_location location = std::source_location::current());
};

/// @brief Function postcondition validator
class Postcondition {
public:
    static void check(bool condition, const char* message,
                     std::source_location location = std::source_location::current());
};

} // namespace voltron::utility::assertions

/// @brief Precondition check macro
#ifdef VOLTRON_ENABLE_CONTRACTS
    #define VOLTRON_PRECONDITION(cond, msg) \
        voltron::utility::assertions::Precondition::check(cond, msg)

    #define VOLTRON_POSTCONDITION(cond, msg) \
        voltron::utility::assertions::Postcondition::check(cond, msg)
#else
    #define VOLTRON_PRECONDITION(cond, msg) ((void)0)
    #define VOLTRON_POSTCONDITION(cond, msg) ((void)0)
#endif
