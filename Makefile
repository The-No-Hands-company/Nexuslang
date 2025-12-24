# NLPL Compiler Test Suite
# Run comprehensive tests on the compiler

TEST_DIR := test_programs/compiler
BUILD_DIR := build
NLPLC := ./nlplc

# Test files
TESTS := \
	test_globals \
	test_globals_complete \
	test_multidim_arrays \
	test_multidim_complete \
	test_range_for \
	test_range_for_complete \
	test_bitwise \
	test_struct_complete \
	test_string_complete

.PHONY: all clean test test-verbose help

all: test

help:
	@echo "NLPL Compiler Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make test         - Run all compiler tests"
	@echo "  make test-verbose - Run tests with verbose output"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make help         - Show this help"

test:
	@echo "Running NLPL compiler tests..."
	@for test in $(TESTS); do \
		echo "Testing $$test..."; \
		$(NLPLC) $(TEST_DIR)/$$test.nlpl -o $(BUILD_DIR)/$$test --run > /dev/null 2>&1 && \
		echo "  ✓ $$test passed" || \
		echo "  ✗ $$test FAILED"; \
	done
	@echo "All tests complete!"

test-verbose:
	@echo "Running NLPL compiler tests (verbose)..."
	@for test in $(TESTS); do \
		echo ""; \
		echo "======================================"; \
		echo "Testing $$test"; \
		echo "======================================"; \
		$(NLPLC) $(TEST_DIR)/$$test.nlpl -o $(BUILD_DIR)/$$test -v --run || exit 1; \
	done
	@echo ""
	@echo "All tests passed!"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)/*
	@echo "Done!"

# Individual test targets
$(TESTS): %:
	$(NLPLC) $(TEST_DIR)/$@.nlpl -o $(BUILD_DIR)/$@ -v --run
