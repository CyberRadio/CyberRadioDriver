import CyberRadioDriver as CRD

if __name__ == "__main__":
    radioObj = CRD.getRadioObject("ndr358",host="192.168.0.10", verbose=True)
    cmd = {"cmd" : "qcfgsys", "params" : {}}
    print(radioObj.sendCommand(json.dumps(cmd)))
    # Uncomment below to setup the Radio Primary infc
    #cmd = {"cmd" : "cfgsys", "params" : { "pri-ip" : "192.168.10.100", "pri-netmask" : "255.255.255.0" }}
    #print(radioObj.sendCommand(json.dumps(cmd)))
    cmd = {"cmd" : "qcfgsys", "params" : {}}
    print(radioObj.sendCommand(json.dumps(cmd)))
