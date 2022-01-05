#Minecraft Utility
### Libraries: mcstatus, pyqtgraph, pyqt5, requests, datetime, json, os, sys

![app image](https://github.com/g-ulrich/pyqt5-mcstatus/blob/main/images/app.png)

### Description:
This single page pyqt5 based app offers current and historical data on players in any given minecraft server (java edition). Enter a valid server URL/ip and discord webhook url for full functionality. 
The webhook and server entries are optional, but the app would not have much purpose without them. Otherwise you can use the portal calculator for helpful guidance on proper coordinates in both overworld and the nether.

### Info
- Unless the send logs checkbox is false all logs with [INFO] will be sent to the discord webhook.
- Player historical data is updated every 5 minutes.
- If there are zero players online discord will not be updated.
- Logs will clear every 200 items.
- all data is saved to the file pyqt5-mcstatus.json
