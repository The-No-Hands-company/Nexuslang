"""
Test cases for the NLPL standard library.
Tests all standard library modules and functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import os
import tempfile
from nlpl.interpreter.interpreter import Interpreter
from nlpl.runtime.runtime import Runtime
from nlpl.stdlib import register_stdlib

class TestStandardLibrary(unittest.TestCase):
    """Test cases for the NLPL standard library."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.runtime = Runtime()
        register_stdlib(self.runtime)
        self.interpreter = Interpreter(self.runtime)
        
        # Create temporary directory for file operations
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_cwd)
        # Clean up temporary files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_math_module(self):
        """Test math module functions."""
        source = """
        # Test constants
        pi as Float = math.PI
        e as Float = math.E
        
        # Test basic arithmetic functions
        abs_val as Integer = math.abs(-42)
        sqrt_val as Float = math.square_root(16)
        pow_val as Integer = math.power(2, 3)
        
        # Test trigonometric functions
        sin_val as Float = math.sine(math.PI / 2)
        cos_val as Float = math.cosine(0)
        tan_val as Float = math.tangent(math.PI / 4)
        
        # Test logarithmic functions
        log_val as Float = math.log(8, 2)
        ln_val as Float = math.ln(math.E)
        
        # Test statistical functions
        numbers as List[Integer] = [1, 2, 3, 4, 5]
        mean_val as Float = math.mean(numbers)
        median_val as Float = math.median(numbers)
        std_dev as Float = math.standard_deviation(numbers)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertAlmostEqual(self.runtime.get_variable("pi"), 3.141592653589793)
        self.assertAlmostEqual(self.runtime.get_variable("e"), 2.718281828459045)
        self.assertEqual(self.runtime.get_variable("abs_val"), 42)
        self.assertEqual(self.runtime.get_variable("sqrt_val"), 4.0)
        self.assertEqual(self.runtime.get_variable("pow_val"), 8)
        self.assertAlmostEqual(self.runtime.get_variable("sin_val"), 1.0)
        self.assertEqual(self.runtime.get_variable("cos_val"), 1.0)
        self.assertAlmostEqual(self.runtime.get_variable("tan_val"), 1.0)
        self.assertEqual(self.runtime.get_variable("log_val"), 3.0)
        self.assertAlmostEqual(self.runtime.get_variable("ln_val"), 1.0)
        self.assertEqual(self.runtime.get_variable("mean_val"), 3.0)
        self.assertEqual(self.runtime.get_variable("median_val"), 3.0)
        self.assertAlmostEqual(self.runtime.get_variable("std_dev"), 1.4142135623730951)
    
    def test_string_module(self):
        """Test string module functions."""
        source = """
        # Test string manipulation
        str1 as String = "hello"
        str2 as String = "world"
        
        # Test case conversion
        upper as String = string.uppercase(str1)
        lower as String = string.lowercase("HELLO")
        title as String = string.title("hello world")
        
        # Test string operations
        length as Integer = string.length(str1)
        concat as String = string.concatenate(str1, " ", str2)
        substr as String = string.substring(str1, 0, 2)
        
        # Test string searching
        contains as Boolean = string.contains("hello world", "world")
        index as Integer = string.index_of("hello world", "world")
        starts_with as Boolean = string.starts_with("hello world", "hello")
        ends_with as Boolean = string.ends_with("hello world", "world")
        
        # Test string replacement
        replaced as String = string.replace("hello world", "world", "there")
        
        # Test string splitting and joining
        words as List[String] = string.split("hello world", " ")
        joined as String = string.join(words, "-")
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("upper"), "HELLO")
        self.assertEqual(self.runtime.get_variable("lower"), "hello")
        self.assertEqual(self.runtime.get_variable("title"), "Hello World")
        self.assertEqual(self.runtime.get_variable("length"), 5)
        self.assertEqual(self.runtime.get_variable("concat"), "hello world")
        self.assertEqual(self.runtime.get_variable("substr"), "he")
        self.assertTrue(self.runtime.get_variable("contains"))
        self.assertEqual(self.runtime.get_variable("index"), 6)
        self.assertTrue(self.runtime.get_variable("starts_with"))
        self.assertTrue(self.runtime.get_variable("ends_with"))
        self.assertEqual(self.runtime.get_variable("replaced"), "hello there")
        self.assertEqual(self.runtime.get_variable("words"), ["hello", "world"])
        self.assertEqual(self.runtime.get_variable("joined"), "hello-world")
    
    def test_io_module(self):
        """Test IO module functions."""
        source = """
        # Test file operations
        content as String = "Hello, World!"
        file_path as String = "test.txt"
        
        # Test writing to file
        io.write(file_path, content)
        
        # Test reading from file
        read_content as String = io.read(file_path)
        
        # Test file existence
        exists as Boolean = io.exists(file_path)
        
        # Test appending to file
        io.append(file_path, "\nAppended content")
        appended_content as String = io.read(file_path)
        
        # Test file deletion
        io.delete(file_path)
        deleted_exists as Boolean = io.exists(file_path)
        
        # Test directory operations
        dir_path as String = "test_dir"
        io.create_directory(dir_path)
        dir_exists as Boolean = io.exists(dir_path)
        files as List[String] = io.list_directory(dir_path)
        
        # Clean up
        io.delete_directory(dir_path)
        dir_deleted_exists as Boolean = io.exists(dir_path)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("read_content"), "Hello, World!")
        self.assertTrue(self.runtime.get_variable("exists"))
        self.assertEqual(self.runtime.get_variable("appended_content"), "Hello, World!\nAppended content")
        self.assertFalse(self.runtime.get_variable("deleted_exists"))
        self.assertTrue(self.runtime.get_variable("dir_exists"))
        self.assertEqual(self.runtime.get_variable("files"), [])
        self.assertFalse(self.runtime.get_variable("dir_deleted_exists"))
    
    def test_system_module(self):
        """Test system module functions."""
        source = """
        # Test system information
        os_name as String = system.os_name()
        os_version as String = system.os_version()
        platform as String = system.platform()
        python_version as String = system.python_version()
        hostname as String = system.hostname()
        
        # Test process information
        pid as Integer = system.process_id()
        current_time as String = system.current_time()
        current_date as String = system.current_date()
        
        # Test environment variables
        env_var as String = "TEST_VAR"
        env_value as String = "test_value"
        system.set_environment_variable(env_var, env_value)
        retrieved_value as String = system.get_environment_variable(env_var)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertIsInstance(self.runtime.get_variable("os_name"), str)
        self.assertIsInstance(self.runtime.get_variable("os_version"), str)
        self.assertIsInstance(self.runtime.get_variable("platform"), str)
        self.assertIsInstance(self.runtime.get_variable("python_version"), str)
        self.assertIsInstance(self.runtime.get_variable("hostname"), str)
        self.assertIsInstance(self.runtime.get_variable("pid"), int)
        self.assertIsInstance(self.runtime.get_variable("current_time"), str)
        self.assertIsInstance(self.runtime.get_variable("current_date"), str)
        self.assertEqual(self.runtime.get_variable("retrieved_value"), "test_value")
    
    def test_collections_module(self):
        """Test collections module functions."""
        source = """
        # Test list operations
        numbers as List[Integer] = [1, 2, 3, 4, 5]
        collections.append(numbers, 6)
        length as Integer = collections.length(numbers)
        first as Integer = collections.first(numbers)
        last as Integer = collections.last(numbers)
        reversed_list as List[Integer] = collections.reverse(numbers)
        
        # Test dictionary operations
        dict1 as Dictionary[String, Integer] = {"a": 1, "b": 2}
        dict2 as Dictionary[String, Integer] = {"c": 3, "d": 4}
        merged_dict as Dictionary[String, Integer] = collections.merge(dictionaries)
        
        # Test set operations
        set1 as Set[Integer] = {1, 2, 3}
        set2 as Set[Integer] = {3, 4, 5}
        union_set as Set[Integer] = collections.union(set1, set2)
        intersection_set as Set[Integer] = collections.intersection(set1, set2)
        difference_set as Set[Integer] = collections.difference(set1, set2)
        
        # Test queue operations
        queue as Queue[Integer] = collections.create_queue()
        collections.enqueue(queue, 1)
        collections.enqueue(queue, 2)
        first_item as Integer = collections.dequeue(queue)
        queue_length as Integer = collections.queue_length(queue)
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        self.assertEqual(self.runtime.get_variable("length"), 6)
        self.assertEqual(self.runtime.get_variable("first"), 1)
        self.assertEqual(self.runtime.get_variable("last"), 6)
        self.assertEqual(self.runtime.get_variable("reversed_list"), [6, 5, 4, 3, 2, 1])
        self.assertEqual(self.runtime.get_variable("merged_dict"), {"a": 1, "b": 2, "c": 3, "d": 4})
        self.assertEqual(self.runtime.get_variable("union_set"), {1, 2, 3, 4, 5})
        self.assertEqual(self.runtime.get_variable("intersection_set"), {3})
        self.assertEqual(self.runtime.get_variable("difference_set"), {1, 2})
        self.assertEqual(self.runtime.get_variable("first_item"), 1)
        self.assertEqual(self.runtime.get_variable("queue_length"), 1)
    
    def test_network_module(self):
        """Test network module functions."""
        source = """
        # Test URL operations
        url as String = "https://example.com/path?param=value"
        parsed_url as Dictionary[String, String] = network.parse_url(url)
        
        # Test URL encoding/decoding
        encoded as String = network.url_encode("Hello, World!")
        decoded as String = network.url_decode(encoded)
        
        # Test DNS operations
        ip as String = network.resolve_dns("example.com")
        
        # Test HTTP operations (commented out to avoid actual network calls)
        # response as Dictionary[String, Any] = network.http_get("https://api.example.com/data")
        # post_response as Dictionary[String, Any] = network.http_post("https://api.example.com/data", {"key": "value"})
        """
        result = self.interpreter.interpret(source)
        
        # Check results
        parsed_url = self.runtime.get_variable("parsed_url")
        self.assertEqual(parsed_url["scheme"], "https")
        self.assertEqual(parsed_url["netloc"], "example.com")
        self.assertEqual(parsed_url["path"], "/path")
        self.assertEqual(parsed_url["query"], "param=value")
        
        self.assertEqual(self.runtime.get_variable("decoded"), "Hello, World!")
        self.assertIsInstance(self.runtime.get_variable("ip"), str)

if __name__ == '__main__':
    unittest.main() 