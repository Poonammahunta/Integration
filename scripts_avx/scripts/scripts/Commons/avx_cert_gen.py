'''script for AppViewX initial setting for root and intermediate cert author:Balakrishnan.S''' 
import sys,os.path,json,ast
import urllib
from configobj import ConfigObj
import requests
import set_path
import logger
lggr = logger.avx_logger('avx')
avx_path = set_path.AVXComponentPathSetting()
location = avx_path.property_path
conf_location=avx_path.conf_file_path
import avx_commons
import signal
signal.signal(signal.SIGINT, avx_commons.sigint_handler)

def get_gwinfo():
    '''Parse required data from properties file'''
    try:
        config = ConfigObj(location + '/appviewx.properties')
        gwurl=config['GATEWAY_BASE_URL']
        gwkey=config['GATEWAY_KEY']
        gwsource=config['SOURCE']
        lggr.info("Parsing from properties file")
        return gwurl,gwkey,gwsource
    except Exception as err:
        lggr.error("error in parsing-Parameters(gateway-url/key/Source) Missing in appviewx.properties file ")
        print ("\033[91mInitial Certificates Generation-Failed \033[0m")
        raise Exception
def get_sessionid(gwurl,gwkey,gwsource):
    '''To get the session ID'''
    try:
        lggr.info("Perfoming Login")
        url="{0}avxapi/acctmgmt-perform-login?gwkey={1}&gwsource={2}".format(gwurl,gwkey,gwsource)
        headers= {'username': 'sudo','password':'74ZB1yoc89G243sl','Content-Type':'application/json'}
        response = requests.post(url, headers=headers,verify=False,timeout=10)
        response=json.loads(response.text)
        if response["response"]["Status"]=="Success":
            lggr.debug("SessionId generated is %s"%response["response"]["SessionId"])
            return response["response"]["SessionId"]
        else:
            return "\033[91m SessionId not generated \033[0m"
    except Exception as err:
        lggr.error("Error in SessionId generation")

        print ("\033[91mInitial Certificates Generation-Failed \033[0m")
        raise Exception
def get_rootvalues(gwurl,gwkey,gwsource,SessionId):
    '''root cert and intermediate generation''' 
    try:
        lggr.info("Initialising root and intermediate cert generation")     
        url1 ='{0}avxapi/cert-ca-settings-save?gwkey={1}&gwsource={2}'.format(gwurl,gwkey,gwsource)
        payload={
        "payload" : {
            "name" : "AppViewX CA",
            "certificateAuthority" : "AppViewX",
            "vendorSpecificSettings" : {
                "rootCertCSRParams" : {
                    "commonName" : "AppViewX CA",
                    "organizationUnit" : "",
                    "organization" : "Payoda Inc",
                    "locality" : "Plano",
                    "country" : "US",
                    "state" : "Texas",
                    "keyType" : "RSA",  
                    "bitLength" : "1024",
                    "mailAddress" : "",
                    "hashFunction" : "SHA256"
                },
                "rootCertValidity" : {
                    "validityInDays" : 7300
                },
                "intermediateCertCSRParams" : {
                    "commonName" : "AppViewX Intermediate CA",
                    "organizationUnit" : "",
                    "organization" : "Payoda Inc",
                    "locality" : "Plano",
                    "country" : "US",
                    "state" : "Texas",
                    "keyType" : "RSA",
                    "bitLength" : "1024",
                    "mailAddress" : "",
                    "hashFunction" : "SHA256"
                },
                "intermediateCertValidity" : {
                    "validityInDays" : 1825
                }
            }
        }
    }
        headers= {'SessionId':SessionId,'Content-Type':'application/json'}
        response = requests.post(url1, headers=headers,data=json.dumps(payload),verify=False,timeout=10)
        response=response.text
        response=json.loads(response)
        if not len(response)==1:
            if response['appStatusCode']=='CERT_CA_SET_NAME_EXSTS':
                lggr.info("Initial Certificates already exists.")
                return "\033[92mInitial Certificates already exists-Successful \033[0m"
            elif response["response"] and not response['message']:
                lggr.info("Cert-Files Generated Successfully.")
                return "\033[92mInitial Certificates Generation-Successful\033[0m"
            elif "Unauthorized access to API cert-ca-settings-save" in response["response"]:
                lggr.error("Error generating Cert-Files.")
                return "\033[91mInitial Certificates Generation-Failed \033[0m"
            else:
                lggr.error("Error in generating Cert-Files.")
                return "\033[91mAVX Initial Certificates Generation-Failed \033[0m"
        else:
            lggr.error("Error generating Cert-Files{0}.".format(response))
            return "\033[91mInitial Certificates Generation-Failed \033[0m"

    except Exception as err:
        lggr.error("Error in recieving response")
        print ("\033[91mInitial Certificates Generation-Failed \033[0m")
        raise Exception
def initialise(call=False):
    try:
        config = ConfigObj(conf_location)
        if "avx_subsystem_certificate" in config['PLUGINS']['ENABLED_PLUGINS'] and "avx_vendor_cert_ca" in config['PLUGINS']['ENABLED_PLUGINS'] or "avx_vendors" in config['PLUGINS']['ENABLED_PLUGINS'] or"avx_subsystems" in config['PLUGINS']['ENABLED_PLUGINS']:
            gwurl,gwkey,gwsource=get_gwinfo()
            SessionId=get_sessionid(gwurl,gwkey,gwsource)
            print (get_rootvalues(gwurl,gwkey,gwsource,SessionId))
        elif call:
            print ("\033[91mcert-mgmt/cert-ca plugins not available\033[0m")
            return
    except Exception:
        return 
if __name__ == "__main__":
    try:
        initialise()
    except Exception as err:
        lggr.error("Initial Certificates Generation-Failed %s",err)
        print ("\033[91mInitial Certificates Generation-Failed \033[0m")

