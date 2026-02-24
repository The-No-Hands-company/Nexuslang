# NLPL Versioning Strategy

**Created:** February 17, 2026  
**Author:** Project Maintainer Clarification

---

## Version Philosophy

NLPL follows a **completion-based versioning** strategy, NOT a traditional semantic versioning approach during development.

### Current State (February 2026)

**What GitHub shows:** v1.1, v1.2 tags  
**What this means:** Early development milestones, NOT production releases  
**Conceptual version:** ~v0.8 or v0.9 (95% feature-complete, not production-ready)

---

## Version 1.0 Definition

**Version 1.0 will be released when:**

1. ✅ **Every feature in MISSING_FEATURES_ROADMAP.md is complete** (Parts 1-10)
2. ✅ **All stdlib modules are production-ready** (not just functional)
3. ✅ **Performance is optimized** (benchmarks competitive with C/Rust)
4. ✅ **LSP is fully functional** (autocomplete, diagnostics, refactoring)
5. ✅ **Manual testing is complete** (every example, every test program runs correctly)
6. ✅ **Documentation is comprehensive** (tutorials, API docs, language spec)
7. ✅ **Build system is robust** (package manager, dependency resolution, CI/CD integration)
8. ✅ **Cross-platform support** (Linux, Windows, macOS, ARM, x86-64)
9. ✅ **Error messages are excellent** (helpful, contextual, suggest fixes)
10. ✅ **Production readiness** (stability, reliability, backwards compatibility guarantees)

**Summary:** v1.0 = **100% complete, feature-complete, production-ready, industrial-strength language**

---

## Development Versioning (Pre-v1.0)

### Current Tags Explanation

The existing GitHub tags (v1.1, v1.2, etc.) represent **development milestones**, not production releases:

- **v1.1**: Early LLVM compiler backend milestone
- **v1.2**: Named parameters + default values feature completion
- **v1.3**: Variadic parameters + trailing blocks
- **v1.4**: Build system core completion

**Recommended interpretation:** Treat these as **v0.1, v0.2, v0.3, v0.4** conceptually.

### Going Forward (Pre-v1.0)

**Option 1: Continue with v1.x tags** (current approach)
- Keep incrementing: v1.5, v1.6, v1.7, etc.
- Document clearly: "Development releases, not production"
- When ready: Jump to **v2.0** as the "true" v1.0 (confusing but maintains continuity)

**Option 2: Restart with v0.x tags** (cleaner but breaks continuity)
- Next release: **v0.9.0** (to reflect 95% completion)
- Final pre-release: **v0.99.0** or **v1.0-rc1**
- Official release: **v1.0.0**
- Breaks continuity with existing v1.1/v1.2 tags

**Option 3: Hybrid - Use dev tags** (recommended)
- Next release: **v1.5-dev** or **v0.9.0-alpha**
- Pre-release: **v1.0-beta**, **v1.0-rc1**, **v1.0-rc2**
- Official release: **v1.0.0**
- Makes it clear these are development builds

---

## Post-v1.0 Versioning

After v1.0 is released, NLPL will follow **semantic versioning**:

### v1.x.y (Stable, Production-Ready)

- **v1.0.0**: Initial production release (all Parts 1-10 complete)
- **v1.0.1, v1.0.2**: Bug fixes, performance improvements (PATCH)
- **v1.1.0, v1.2.0**: New stdlib modules, minor features (MINOR)
- **v2.0.0**: Breaking changes, major language redesign (MAJOR)

### Post-v1.0 Feature Additions (Parts 11-16)

Features from the extended roadmap (AI integration, metaprogramming, actor model, etc.) will be added as **MINOR versions**:

- **v1.1.0**: LSP enhancements + profiling tools (Part 15.1)
- **v1.2.0**: Contract programming (Part 13.1)
- **v1.3.0**: Static reflection (Part 12.1)
- **v1.4.0**: Actor model concurrency (Part 14.1)
- **v2.0.0**: AI ambiguity resolution (Part 11.1 - possibly breaking change to parser behavior)

---

## Roadmap Timeline Interpretation

When the roadmap says:

- **"Post-v1.0"**: After the **complete, production-ready** v1.0 release
- **"Year 2"**: Approximately 2027-2028 (1-2 years after v1.0 release)
- **"Year 3"**: 2028-2029 (2-3 years after v1.0)

**Note:** Given that NLPL is currently ~95% complete (per MISSING_FEATURES_ROADMAP.md), v1.0 release is likely **Q3-Q4 2026** (assuming 3-6 months for remaining work: LSP, stdlib expansion, performance tuning, manual testing).

---

## Example Timeline (Projected)

| Date | Version | Milestone |
|------|---------|-----------|
| **Feb 2026** | v1.4 (current) | Build system complete, hardware access done |
| **Mar 2026** | v1.5-dev | LSP foundation complete |
| **Apr 2026** | v1.6-dev | Stdlib expansion (70+ modules) |
| **May 2026** | v1.7-dev | Performance optimization (2x-3x C speed) |
| **Jun 2026** | v1.8-dev | Cross-platform testing (Windows/macOS) |
| **Jul 2026** | v1.0-beta | Feature freeze, bug fixing only |
| **Aug 2026** | v1.0-rc1 | Release candidate 1 |
| **Sep 2026** | **v1.0.0** | **OFFICIAL PRODUCTION RELEASE** |
| **Q4 2026** | v1.0.1, v1.0.2 | Bug fixes, stability improvements |
| **Q1 2027** | v1.1.0 | Built-in profiling (Part 15.1) |
| **Q2 2027** | v1.2.0 | Contract programming (Part 13.1) |
| **Q3-Q4 2027** | v1.3.0 | Static reflection (Part 12.1) |
| **2028** | v1.4.0+ | Actor model, macro system, etc. |
| **2028-2029** | v2.0.0 | AI ambiguity resolution (Part 11.1) |

---

## Compatibility Guarantees

### Pre-v1.0 (Current State)

- **No guarantees**: Breaking changes allowed
- **Best effort**: Minimize disruption
- **Migration guides**: Provided for major syntax changes

### Post-v1.0

- **Backwards compatibility**: Within v1.x series (v1.0 code runs on v1.9)
- **Deprecation cycle**: 2 minor versions (deprecate in v1.3, remove in v1.5)
- **Breaking changes**: Only in major versions (v2.0, v3.0)

---

## Summary

**Current versioning is confusing because:**
- GitHub tags (v1.1, v1.2) suggest production-ready software
- Reality: NLPL is 95% complete but not yet production-ready
- Intended v1.0: 100% complete, feature-complete, production-ready

**Going forward:**
1. Continue using v1.x tags with `-dev` or `-alpha` suffix
2. Reserve **v1.0.0** for the official production release
3. After v1.0.0, follow semantic versioning strictly
4. Post-v1.0 features (Parts 11-16) are MINOR or MAJOR version bumps

**Projected v1.0.0 release:** Q3 2026 (September 2026)  
**Post-v1.0 features:** 2027-2029 (v1.1.0 through v2.0.0)

**Key takeaway:** The roadmap's "Post-v1.0" means "after the complete, production-ready release", which is still **3-6 months away** despite GitHub showing v1.x tags.
