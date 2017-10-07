import sys
sys.path.append("D:\\POO\\Py_work")

from mulpy_test import mount_details
'''import unittest
 
class TestUM(unittest.TestCase):
 
    def setUp(self):
        pass
    def test_mount_details(self):
        result = mount_details()
        self.assertIsInstance(result,list)
        self.assertIsInstance(result[4],str)

    def test_rootex(self):
        result = mount_details()
        for line in result:
            if line[1] == "":
                self.assertEqual(line[2],'')
if __name__ == '__main__':
    unittest.main()'''

'''import pytest

class Test:
    def test_mount(self):
        result = mount_details()
        #print result
        assert result[4] == '(good gal and that is what)'

    def test2(self):
        print "I'm the test 2"'''

import pytest
@pytest.fixture()
def sample_test(testdir):
    testdir.makepyfile("""
        def test_pass():
            assert 1 == 1
        def test_fail():
            assert 1 == 2
""") 
    return testdir


def test_with_nice(sample_test):
    result = sample_test.runpytest('-v')
    print result
    
        
