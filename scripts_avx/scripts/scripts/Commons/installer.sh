#!/bin/bash

control_c() {
    echo
    echo 'Keyboard Interrupt'
    rm -rf Python/ __pycache__/ Plugins/ conf/ config_parser.py install.py configuration_generation.py conf_data.p .conf_hash.txt
    exit
}

trap control_c SIGINT

if [ "$EUID" = 0 ]
    then 
        echo "$(tput setaf 1)Root user cannot install AppViewX!$(tput sgr 0)"
        exit
fi

ins_file=$(ls | grep -i 'AppViewX' | grep 'tar.gz' | grep -iv 'license' | grep -iv 'conf')
size=$(ls | grep -i 'AppViewX' | grep 'tar.gz' | grep -iv 'license' | grep -iv 'conf' | wc -l)

if [ $size -ne 1 ]
    then
        while true
        do
            read -e -p 'Enter AppViewX installer path : ' ins_file
            if test -e "$ins_file"
                then
                    echo $ins_file | grep -i 'AppViewX' | grep 'tar.gz' | grep -iv 'license' > /dev/null 
                    if [ "$?" == "0"  ]
                        then break
                        else
                            echo "$(tput setaf 1)Not a valid installer file!$(tput sgr 0)"
                    fi
                else
                    echo "$(tput setaf 1)File not found$(tput sgr 0)"
            fi
        done
fi

echo "$(tput setaf 2)Extracting Python$(tput sgr 0)"
tar -xf $ins_file Python/ scripts/Commons/config_parser.py scripts/Commons/install.py scripts/Commons/configuration_generation.py
cp scripts/Commons/config_parser.py .
cp scripts/Commons/install.py .
cp scripts/Commons/configuration_generation.py .
rm -rf scripts
ins_file=$(readlink -f $ins_file)
chmod +x install.py
./install.py $ins_file
rm -rf Python/ __pycache__/ Plugins/ conf/ config_parser.py install.py configuration_generation.py conf_data.p .conf_hash.txt
