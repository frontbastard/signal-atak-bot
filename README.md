# Signal Bot

## How to install
### Create and connect a virtual environment
1. `python -m venv .venv`
1. `source .venv/bin/activate`

### Install requirements
1. `pip install -r requirements.txt`

### Run the program
1. `python bot.py 55.755825 37.617298 tank`  
To see the result you have to install the ATAK-CIV application (see the `Install the application ATAC` chapter)

## .env variables
By default, the data for connecting to the public server is used (see Public Connection Details), but if you need to customise the connection data, you can rename the file `.env.sample` to `.env` and fill in the variables.

## Public Connection Details
**TAK Host**: 137.184.101.250  
**TAK Port**: 8087

---

## Install the application ATAC
### Download the app
On your phone (Android) install the application by this link https://play.google.com/store/apps/details?id=com.atakmap.app.civ&pli=1

### Create a new connection to the server
1. Press the `≣` icon to get to the main menu
1. Find the gear icon named `Settings`
1. Go to `Network settings`
1. Go to `Setting up a network connection`
1. Go to `Manage your server connection`
1. Click on the icon with three vertical dots `⋮` and press `Add`
   - Fill in the name: ATAK
   - Fill in the address: 137.184.101.250
   - Open the `Advanced options` and specify the `TCP` and the `server port 8087`
