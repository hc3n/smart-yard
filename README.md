# Project Structure

* `remote_device_node.py` - work with sensors and devices on remote nodes
* `logic.py` - (optional) automatic control
* `bridge.py` - bridge between components
* `api_server.py` - REST API server

## C4 model (context layer)
<img width="881" height="876" alt="C4_LVL1_NEW drawio" src="https://github.com/user-attachments/assets/c86f0ce7-4115-4cab-93da-f13ab8988607" />

## General template for broker topic structure
* {cluster}/{category}/{device}/{action/state}
* cluster - is any room/space/object
* category - sensor/system/lora/cmd
* device - specific device

## Web UI (Dashboard)
<img width="1280" height="911" alt="telegram-cloud-photo-size-2-5208470796953656815-y" src="https://github.com/user-attachments/assets/713308fc-6ebc-45ac-bdd2-0268387b95a3" />

  
