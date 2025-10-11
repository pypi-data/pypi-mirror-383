import unittest
from nikil_test_math import nikil_test_math

class TestMath(unittest.TestCase):
    def test_add(self):
        self.assertEqual(nikil_test_math.add(5, 3), 8)
        self.assertEqual(nikil_test_math.add(-1, 1), 0)
        self.assertEqual(nikil_test_math.add(0, 0), 0)
        
    def test_subtract(self):
        self.assertEqual(nikil_test_math.subtract(10, 5, 2), 3)
        self.assertEqual(nikil_test_math.subtract(0, 0, 0), 0)
        self.assertEqual(nikil_test_math.subtract(5, 10, -5), 0)
        
    def test_multiply(self):
        self.assertEqual(nikil_test_math.multiply(4, 5), 20)
        self.assertEqual(nikil_test_math.multiply(0, 100), 0)
        self.assertEqual(nikil_test_math.multiply(-2, 3), -6)
        
if __name__ == '__main__':
    unittest.main()