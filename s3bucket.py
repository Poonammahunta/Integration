f = "D:\\POO\\medical"
import os
import zipfile

for root,dir,files in os.walk(f):
    for item in [os.path.join(root,name)for name in files if name.endswith(".zip")]:
        print item
        zipfile.ZipFile(item).extractall('Give path where to extract the zipfile')
