#include <voltron/utility/compiler/compile_time_counter.h>
#include <iostream>

namespace voltron::utility::compiler {

CompileTimeCounter& CompileTimeCounter::instance() {
    static CompileTimeCounter instance;
    return instance;
}

void CompileTimeCounter::initialize() {
    enabled_ = true;
    std::cout << "[CompileTimeCounter] Initialized\n";
}

void CompileTimeCounter::shutdown() {
    enabled_ = false;
    std::cout << "[CompileTimeCounter] Shutdown\n";
}

bool CompileTimeCounter::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::compiler
