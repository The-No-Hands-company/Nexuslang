#include "voltron/utility/error/exception_context.h"
#include <iostream>

namespace voltron::utility::error {

std::vector<std::string> ExceptionContext::getKeys() const {
    std::vector<std::string> keys;
    keys.reserve(context_.size());
    for (const auto& [key, _] : context_) {
        keys.push_back(key);
    }
    return keys;
}

void ExceptionContext::print(std::ostream& os) const {
    if (context_.empty()) {
        os << "No context data\n";
        return;
    }

    os << "Context data:\n";
    for (const auto& [key, value] : context_) {
        os << "  " << key << ": [value]\n";  // Can't print std::any directly
    }
}

void ContextualException::printFull(std::ostream& os) const {
    os << "\n=== Contextual Exception ===\n";
    os << "Message: " << message_ << "\n";
    os << "Location: " << location_.file_name() << ":" << location_.line()
       << " in " << location_.function_name() << "\n";
    context_.print(os);
    os << "============================\n\n";
}

} // namespace voltron::utility::error
