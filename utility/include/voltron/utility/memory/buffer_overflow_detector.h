#pragma once

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>

namespace voltron::utility::memory {

/// @brief Canary value for detecting buffer overflows
constexpr uint32_t CANARY_VALUE = 0xDEADBEEF;
constexpr size_t CANARY_SIZE = sizeof(uint32_t);

/// @brief Buffer with canary values for overflow detection
template<typename T>
class GuardedBuffer {
public:
    explicit GuardedBuffer(size_t capacity)
        : capacity_(capacity)
        , size_(0)
    {
        // Allocate: [front_canary][data][back_canary]
        size_t total_size = CANARY_SIZE + (capacity * sizeof(T)) + CANARY_SIZE;
        raw_buffer_ = new uint8_t[total_size];

        // Set canaries
        setCanary(raw_buffer_, CANARY_VALUE);
        setCanary(raw_buffer_ + CANARY_SIZE + (capacity * sizeof(T)), CANARY_VALUE);

        // Data pointer
        data_ = reinterpret_cast<T*>(raw_buffer_ + CANARY_SIZE);
    }

    ~GuardedBuffer() {
        checkCanaries();
        delete[] raw_buffer_;
    }

    GuardedBuffer(const GuardedBuffer&) = delete;
    GuardedBuffer& operator=(const GuardedBuffer&) = delete;

    T& operator[](size_t index) {
        if (index >= capacity_) {
            throw std::out_of_range("GuardedBuffer index out of range");
        }
        return data_[index];
    }

    const T& operator[](size_t index) const {
        if (index >= capacity_) {
            throw std::out_of_range("GuardedBuffer index out of range");
        }
        return data_[index];
    }

    T* data() { return data_; }
    const T* data() const { return data_; }

    size_t capacity() const { return capacity_; }
    size_t size() const { return size_; }

    void push_back(const T& value) {
        if (size_ >= capacity_) {
            throw std::out_of_range("GuardedBuffer capacity exceeded");
        }
        data_[size_++] = value;
    }

    void checkCanaries() const {
        uint32_t front_canary = getCanary(raw_buffer_);
        uint32_t back_canary = getCanary(raw_buffer_ + CANARY_SIZE + (capacity_ * sizeof(T)));

        if (front_canary != CANARY_VALUE) {
            throw std::runtime_error("Front canary corrupted! Buffer underflow detected.");
        }
        if (back_canary != CANARY_VALUE) {
            throw std::runtime_error("Back canary corrupted! Buffer overflow detected.");
        }
    }

private:
    void setCanary(uint8_t* location, uint32_t value) {
        std::memcpy(location, &value, sizeof(uint32_t));
    }

    uint32_t getCanary(const uint8_t* location) const {
        uint32_t value;
        std::memcpy(&value, location, sizeof(uint32_t));
        return value;
    }

    uint8_t* raw_buffer_;
    T* data_;
    size_t capacity_;
    size_t size_;
};

/// @brief RAII wrapper to check buffer integrity on scope exit
template<typename T>
class BufferIntegrityChecker {
public:
    explicit BufferIntegrityChecker(GuardedBuffer<T>& buffer)
        : buffer_(buffer)
    {}

    ~BufferIntegrityChecker() {
        buffer_.checkCanaries();
    }

private:
    GuardedBuffer<T>& buffer_;
};

} // namespace voltron::utility::memory
