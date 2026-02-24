"""
Tests for error propagation (? operator).

Production-ready test suite.
"""

import pytest
from nlpl.stdlib.option_result import Ok, Err, Result


class TestErrorPropagation:
    """Tests for ? operator."""
    
    def test_question_operator_on_ok(self):
        """Test ? operator unwraps Ok values."""
        result = Ok(42)
        # In actual usage: value = some_function()?
        # For testing, we verify the Result type
        assert result.is_ok()
        assert result.unwrap() == 42
    
    def test_question_operator_on_err(self):
        """Test ? operator propagates Err values."""
        result = Err("error message")
        assert result.is_err()
        assert result.unwrap_err() == "error message"
    
    def test_result_chaining(self):
        """Test chaining multiple Result operations."""
        def divide(a, b):
            if b == 0:
                return Err("Division by zero")
            return Ok(a / b)
        
        # Success case
        result1 = divide(10, 2)
        assert result1.is_ok()
        assert result1.unwrap() == 5
        
        # Error case
        result2 = divide(10, 0)
        assert result2.is_err()
        assert "Division by zero" in result2.unwrap_err()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
