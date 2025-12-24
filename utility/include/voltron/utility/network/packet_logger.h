#pragma once

#include <string>
#include <vector>

namespace voltron::utility::network {

/**
 * @brief Log network packets
 * 
 * TODO: Implement comprehensive packet_logger functionality
 */
class PacketLogger {
public:
    static PacketLogger& instance();

    /**
     * @brief Initialize packet_logger
     */
    void initialize();

    /**
     * @brief Shutdown packet_logger
     */
    void shutdown();

    /**
     * @brief Check if enabled
     */
    bool isEnabled() const;

private:
    PacketLogger() = default;
    ~PacketLogger() = default;
    
    bool enabled_ = false;
};

} // namespace voltron::utility::network
