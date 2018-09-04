from ConfigParser import SafeConfigParser
parser = SafeConfigParser()
parser.read('p1_changelog')

print parser.get('Issue Tracker','id')
