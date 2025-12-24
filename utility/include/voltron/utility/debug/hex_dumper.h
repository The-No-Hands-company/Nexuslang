#pragma once

#include <iostream>
#include <iomanip>
#include <cstdint>
#include <cstring>

namespace voltron::utility::debug {

/// @brief Hexadecimal memory dump utility
class HexDumper {
public:
    /// Dump memory region in hex format
    static void dump(const void* data, size_t size, std::ostream& os = std::cout);

    /// Dump with custom bytes per line
    static void dump(const void* data, size_t size, size_t bytes_per_line, std::ostream& os = std::cout);

    /// Dump with ASCII representation
    static void dumpWithAscii(const void* data, size_t size, std::ostream& os = std::cout);
};

} // namespace voltron::utility::debug
