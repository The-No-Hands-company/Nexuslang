#include <voltron/utility/config/config_schema_validator.h>
#include <iostream>

namespace voltron::utility::config {

ConfigSchemaValidator& ConfigSchemaValidator::instance() {
    static ConfigSchemaValidator instance;
    return instance;
}

void ConfigSchemaValidator::initialize() {
    enabled_ = true;
    std::cout << "[ConfigSchemaValidator] Initialized\n";
}

void ConfigSchemaValidator::shutdown() {
    enabled_ = false;
    std::cout << "[ConfigSchemaValidator] Shutdown\n";
}

bool ConfigSchemaValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::config
