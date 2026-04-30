/*
 * nxl_runtime.h -- Public API for the NexusLang native runtime library (libNXL).
 *
 * This is the canonical include path.  The matching implementation lives in
 * src/nexuslang/stdlib_native/src/.
 *
 * Convenience re-export: this file includes the full runtime API defined in
 * nlpl_runtime.h, keeping both include-path variants working during the
 * prefix migration from "nlpl_" to "nxl_".
 *
 * Build:  cmake -S src/nexuslang/stdlib_native -B build/stdlib_native
 *               && cmake --build build/stdlib_native
 *
 * Link:   clang ... -Lbuild/stdlib_native -lNXL -lm
 */

#ifndef NXL_RUNTIME_H
#define NXL_RUNTIME_H

#include "nlpl_runtime.h"

#endif /* NXL_RUNTIME_H */
