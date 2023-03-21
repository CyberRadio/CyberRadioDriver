import CyberRadioDriver as CRD
import json

radioObj = CRD.getRadioObject("ndr358", host="192.168.0.10", verbose=True)

# setup our source infmoation for the 10G ports
radioObj.sendCommand(json.dumps({"cmd" : "cfge10g", "params" : { "link": 0, "ip" : "10.1.10.100","port" : 4991}}))
radioObj.sendCommand(json.dumps({"cmd" : "cfge10g", "params" : { "link": 1, "ip" : "10.1.11.100","port" : 4992}}))
radioObj.sendCommand(json.dumps({"cmd" : "cfge10g", "params" : { "link": 2, "ip" : "10.1.12.100","port" : 4993}}))
radioObj.sendCommand(json.dumps({"cmd" : "cfge10g", "params" : { "link": 3, "ip" : "10.1.13.100","port" : 4994}}))
# setup multiple destinations for the data to go to over the 10G ports
radioObj.sendCommand(json.dumps({"cmd" : "e10g", "params" : { "link" : 0, "dest" : 0, "ip" : "10.1.10.1", "port" : 4991, "mac" : "f8:f2:1e:43:d4:b8"}}))
radioObj.sendCommand(json.dumps({"cmd" : "e10g", "params" : { "link" : 1, "dest" : 0, "ip" : "10.1.11.1", "port" : 4992, "mac" : "f8:f2:1e:43:d4:b9"}}))
radioObj.sendCommand(json.dumps({"cmd" : "e10g", "params" : { "link" : 2, "dest" : 0, "ip" : "10.1.12.1", "port" : 4993, "mac" : "f8:f2:1e:52:ef:5c"}}))
radioObj.sendCommand(json.dumps({"cmd" : "e10g", "params" : { "link" : 3, "dest" : 0, "ip" : "10.1.13.1", "port" : 4994, "mac" : "f8:f2:1e:52:ef:5d"}}))
# setup the tuners
radioObj.sendCommand(json.dumps({"cmd" : "tuner", "params": {"id": 0, "freq" : 910e6, "enable" : True }}))
radioObj.sendCommand(json.dumps({"cmd" : "tuner", "params": {"id": 1, "freq" : 910e6, "enable" : True }}))
radioObj.sendCommand(json.dumps({"cmd" : "tuner", "params": {"id": 2, "freq" : 910e6, "enable" : True }}))
radioObj.sendCommand(json.dumps({"cmd" : "tuner", "params": {"id": 3, "freq" : 910e6, "enable" : True }}))
# setup the WBDDCs to source data from a specific tuner and send to a specific destination at filter 40 (80M)
radioObj.sendCommand(json.dumps({"cmd" : "wbddc", "params": {"id": 0, "filter" : 40, "enable" : True, "link" : 0, "dest" : 0, "rfch" : "0"}}))
radioObj.sendCommand(json.dumps({"cmd" : "wbddc", "params": {"id": 1, "filter" : 40, "enable" : True, "link" : 1, "dest" : 0, "rfch" : "1"}}))
radioObj.sendCommand(json.dumps({"cmd" : "wbddc", "params": {"id": 2, "filter" : 40, "enable" : True, "link" : 2, "dest" : 0, "rfch" : "2"}}))
radioObj.sendCommand(json.dumps({"cmd" : "wbddc", "params": {"id": 3, "filter" : 40, "enable" : True, "link" : 3, "dest" : 0, "rfch" : "3"}}))
