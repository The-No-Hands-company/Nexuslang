#include "voltron/utility/debug/hex_dumper.h"

namespace voltron::utility::debug {

void HexDumper::dump(const void* data, size_t size, std::ostream& os) {
    dump(data, size, 16, os);
}

void HexDumper::dump(const void* data, size_t size, size_t bytes_per_line, std::ostream& os) {
    const uint8_t* bytes = static_cast<const uint8_t*>(data);

    os << std::hex << std::setfill('0');

    for (size_t i = 0; i < size; i += bytes_per_line) {
        // Address
        os << std::setw(8) << i << ": ";

        // Hex bytes
        for (size_t j = 0; j < bytes_per_line; ++j) {
            if (i + j < size) {
                os << std::setw(2) << static_cast<int>(bytes[i + j]) << " ";
            } else {
                os << "   ";
            }
        }

        os << "\n";
    }

    os << std::dec;
}

void HexDumper::dumpWithAscii(const void* data, size_t size, std::ostream& os) {
    const uint8_t* bytes = static_cast<const uint8_t*>(data);
    constexpr size_t bytes_per_line = 16;

    os << std::hex << std::setfill('0');

    for (size_t i = 0; i < size; i += bytes_per_line) {
        // Address
        os << std::setw(8) << i << ": ";

        // Hex bytes
        for (size_t j = 0; j < bytes_per_line; ++j) {
            if (i + j < size) {
                os << std::setw(2) << static_cast<int>(bytes[i + j]) << " ";
            } else {
                os << "   ";
            }
        }

        os << " | ";

        // ASCII representation
        for (size_t j = 0; j < bytes_per_line; ++j) {
            if (i + j < size) {
                uint8_t byte = bytes[i + j];
                if (byte >= 32 && byte <= 126) {
                    os << static_cast<char>(byte);
                } else {
                    os << ".";
                }
            }
        }

        os << "\n";
    }

    os << std::dec;
}

} // namespace voltron::utility::debug
