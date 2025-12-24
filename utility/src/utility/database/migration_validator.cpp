#include <voltron/utility/database/migration_validator.h>
#include <iostream>

namespace voltron::utility::database {

MigrationValidator& MigrationValidator::instance() {
    static MigrationValidator instance;
    return instance;
}

void MigrationValidator::initialize() {
    enabled_ = true;
    std::cout << "[MigrationValidator] Initialized\n";
}

void MigrationValidator::shutdown() {
    enabled_ = false;
    std::cout << "[MigrationValidator] Shutdown\n";
}

bool MigrationValidator::isEnabled() const {
    return enabled_;
}

} // namespace voltron::utility::database
