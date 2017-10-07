import xml.etree.ElementTree as ET
file_path = "D:\\POO\\Py_work\\test.xml"

tree = ET.ElementTree(file= 'test.xml')
root = tree.getroot()


for child in root:
    print child.attrib
        
        
    
