import re

def get_pid():
    f = open("C:\\Users\\pmahunta\\Desktop\\new\\cat\\793F_2013C_3934695-54_total_mod.txt","r")
    pid_list = []
    li_dic = {}
    fr = f.readlines()
    for item in fr:
        match = re.search(r'PID=0x(\w*); SID=0x(\w*)',item)
        if match:
            pid_list.append(match.group(1,2))

    for item in pid_list:
        if item[1] in li_dic:
            li_dic[item[1]].append([item[0]])
        else:
            li_dic[item[1]] = [item[0]]
    return li_dic
        
            
def fin():
    x = get_pid()
    fin_pid = []
    for item in x:
        fin_pid.append(x[item].rstrip("0"))
    print fin_pid

'''def file_name():
    f = open("C:\\Users\\pmahunta\\Desktop\\new\\cat\\793F_2013C_3934695-54_total_mod.txt","r")
    fr = f.readlines()
    for item in fr:
        match = re.search(r'Version=0x(\w*); Config Part No.=0x(\w*)',item)
        if match:
            A = match.group(1).decode("hex").lstrip("0")
            B = match.group(2).decode("hex").rstrip("\x00")
    return A,B'''
        
'''def CDL_ECM():
    X,Y = file_name()
    D,E = get_pid()
    G = fin()
    test = ""
    test1 = "<cdl_map param= "
    new_f = open(Y+'_'+X+".xml",'w+')
    for item in D:
        for it in G:
            test = test1+"PID-"+item +"pid= "+it+"enable= ""1"" enable_read= ""1"" enable_write= ""1"" value= ""0""/>"
        new_f.write(test)
    new_f.close()'''  
            



fin()

            




            
            


    
        
    

