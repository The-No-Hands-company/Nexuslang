#pragma once

#include <string>
#include <vector>
#include <functional>
#include <source_location>

namespace voltron::utility::protocol {

/**
 * @brief Log network packets for analysis
 * 
 * Part of the Voltron C++ Utility Toolkit - comprehensive diagnostic infrastructure
 * for professional C++23 development.
 * 
 * @category Protocol
 * @version 1.0.0
 */
class PacketCaptureLogger {
public:
    /**
     * @brief Get singleton instance
     */
    static PacketCaptureLogger& instance();

    /**
     * @brief Initialize the utility
     * @param config Optional configuration parameters
     */
    void initialize(const std::string& config = "");

    /**
     * @brief Shutdown the utility and cleanup resources
     */
    void shutdown();

    /**
     * @brief Check if the utility is currently enabled
     */
    bool isEnabled() const;

    /**
     * @brief Enable the utility
     */
    void enable();

    /**
     * @brief Disable the utility
     */
    void disable();

    /**
     * @brief Get utility statistics/status
     */
    std::string getStatus() const;

    /**
     * @brief Reset utility state
     */
    void reset();

private:
    PacketCaptureLogger() = default;
    ~PacketCaptureLogger() = default;
    
    // Non-copyable, non-movable
    PacketCaptureLogger(const PacketCaptureLogger&) = delete;
    PacketCaptureLogger& operator=(const PacketCaptureLogger&) = delete;
    PacketCaptureLogger(PacketCaptureLogger&&) = delete;
    PacketCaptureLogger& operator=(PacketCaptureLogger&&) = delete;

    bool enabled_ = false;
    std::string config_;
};

} // namespace voltron::utility::protocol
