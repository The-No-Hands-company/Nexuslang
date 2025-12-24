#include <voltron/utility/resource/file_handle_tracker.h>
#include <iostream>

namespace voltron::utility::resource {

FileHandleTracker& FileHandleTracker::instance() {
    static FileHandleTracker instance;
    return instance;
}

void FileHandleTracker::initialize() {
    enabled_ = true;
    std::cout << "[FileHandleTracker] Initialized\n";
}

void FileHandleTracker::shutdown() {
    enabled_ = false;
    std::cout << "[FileHandleTracker] Shutdown\n";
}

bool FileHandleTracker::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::resource
