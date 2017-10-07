import os 
import sys
current_directory = os.path.dirname(os.path.realpath(__file__))

class Get_dependencies():

	def __init__(self):
		pass

	def open_dependencies_file(self,file_name):
		
		if os.path.exists(file_name):
			with open(file_name,'r')  as in_file:
				dependencies_content = in_file.readlines()
			return dependencies_content
		else:
			return None

	def create_dependencies_input(self,dependencies_content):

		plugin_dependencies = dict()
		plugins = list()
		for content in dependencies_content:
			if '>=' in content:
				plugin = content.split('>=')[0]
				plugin = plugin.strip(' ')
				plugin = plugin.strip('\n')
				version = content.split('>=')[1]
				version = version.strip(' ')
				version = version.strip('\n')
				plugin_dependencies[plugin] = dict()
				plugin_dependencies[plugin]['min'] = version
				plugin_dependencies[plugin]['max'] = 'None'
			elif '>=' not in content and '>' in content:
				plugin = content.split('>')[0]
				plugin = plugin.strip(' ')
				plugin = plugin.strip('\n')
				version = content.split('>')[1]
				version = version.strip(' ')
				version = version.strip('\n')
				plugin_dependencies[plugin] = dict()
				plugin_dependencies[plugin]['min'] = version
				plugin_dependencies[plugin]['max'] = 'None'
			elif '<='  in content:
				plugin = content.split('<=')[0]
				plugin = plugin.strip(' ')
				plugin = plugin.strip('\n')
				version = content.split('<=')[1]
				version = version.strip(' ')
				version = version.strip('\n')
				plugin_dependencies[plugin] = dict()
				plugin_dependencies[plugin]['max'] = version
				plugin_dependencies[plugin]['min'] = 'None'
			elif '<='  not in content and '<' in content:
				plugin = content.split('<')[0]
				plugin = plugin.strip(' ')
				plugin = plugin.strip('\n')
				version = content.split('<')[1]
				version = version.strip(' ')
				version = version.strip('\n')
				plugin_dependencies[plugin] = dict()
				plugin_dependencies[plugin]['max'] = version
				plugin_dependencies[plugin]['min'] = 'None'
			elif '=' in content or '==' in content:
				plugin = content.split('=')[0]
				plugin = plugin.strip(' ')
				plugin = plugin.strip('\n')
				version = content.split('=')[1]
				version = version.strip(' ')
				version = version.strip('\n')
				plugin_dependencies[plugin] = dict()
				plugin_dependencies[plugin]['min'] = version
				plugin_dependencies[plugin]['max'] = version
		return plugin_dependencies

	def obtain_plugin_dependencies(self,file_name):

		try:
			file_content = self.open_dependencies_file(file_name)
			if file_content:
				plugin_dependencies = self.create_dependencies_input(file_content)
				return (plugin_dependencies)
		except Exception as e:
			print (e)
			sys.exit(1)

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		plugin_name = sys.argv[1]
		plugin_path = current_directory + '/../../Plugins/' + plugin_name + '/' + plugin_name + '_dependencies'
		Get_dependencies.obtain_plugin_dependencies(Get_dependencies(),plugin_path)

