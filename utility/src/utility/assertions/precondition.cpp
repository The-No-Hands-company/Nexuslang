#include "voltron/utility/assertions/precondition.h"
#include <iostream>
#include <stacktrace>
#include <stdexcept>

namespace voltron::utility::assertions {

void Precondition::check(bool condition, const char* message,
                        std::source_location location) {
    if (!condition) {
        std::cerr << "\n=== PRECONDITION VIOLATION ===\n";
        std::cerr << "Message: " << message << "\n";
        std::cerr << "Location: " << location.file_name() << ":" << location.line()
                  << " in " << location.function_name() << "\n";

        auto trace = std::stacktrace::current(1, 20);
        std::cerr << "\nStack trace:\n" << trace << "\n";
        std::cerr << "==============================\n\n";

        throw std::logic_error("Precondition violated");
    }
}

void Postcondition::check(bool condition, const char* message,
                         std::source_location location) {
    if (!condition) {
        std::cerr << "\n=== POSTCONDITION VIOLATION ===\n";
        std::cerr << "Message: " << message << "\n";
        std::cerr << "Location: " << location.file_name() << ":" << location.line()
                  << " in " << location.function_name() << "\n";

        auto trace = std::stacktrace::current(1, 20);
        std::cerr << "\nStack trace:\n" << trace << "\n";
        std::cerr << "===============================\n\n";

        throw std::logic_error("Postcondition violated");
    }
}

} // namespace voltron::utility::assertions
