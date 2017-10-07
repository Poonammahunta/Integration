#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

control_c() {
    echo
    echo 'Keyboard Interrupt'
    rm -rf Python scripts __pycache__ upgrade.py config_parser.py upgrade.py conf install.py install.log appviewx.conf conf_data.p
    exit
}

trap control_c SIGINT

if [[ $EUID -eq 0 ]]; 
then   
   echo -e "${RED}Root user is not allowed to install AppViewX${NC}"
exit 1
fi
file_sensor=`find . -name 'AppViewX_Patch.tar.gz' -o -name 'appviewx_*_upgrade_file.tar.gz'`
file_sensor=($file_sensor)
if [[ ${#file_sensor[@]} -eq 1 ]];
then
   upgrade_file=${file_sensor[0]}
else
   echo -n -e "${GREEN}Enter the AVX upgrade_file path ${NC}"
   read -e -p ":" upgrade_file
   while [[ ! $upgrade_file == *tar.gz ]] || [[ ! -f $upgrade_file ]]
   do 
      echo -e ${RED}${upgrade_file}' file not found and It should be tar file'${NC}
      echo -n -e ${GREEN}'Enter the AVX upgrade_file path '${NC}
      read -e -p ":" upgrade_file
   done
fi
upgrade_file_path=`readlink -f $upgrade_file`
echo "$(tput setaf 2)Extracting Python$(tput sgr 0)"
tar -xf $upgrade_file Python scripts conf
cp scripts/upgrade/upgrade.py .
cp scripts/Commons/install.py .
cp scripts/Commons/config_parser.py .
cp conf/appviewx.conf .
chmod +x upgrade.py
Python/bin/python upgrade.py ${upgrade_file_path}
rm -rf Python scripts __pycache__ upgrade.py config_parser.py upgrade.py conf install.py install.log appviewx.conf conf_data.p
