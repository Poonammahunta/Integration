import xml.etree.cElementTree as ET
tree = ET.parse("C:\\Users\\pmahunta\\Desktop\\new\\test.xml")
tree.getroot()
for elem in tree.find('App_ID'):
    print elem.attrib


