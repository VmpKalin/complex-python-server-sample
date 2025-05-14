# Local System Setup

## Requirements
- Python 3.11 (or newer)
  - Install 3.11 through the Microsoft App Store
- Pip

  `python -m ensurepip`

- VirtualEnv

  `pip install virtualenv`

# Project Setup
## 1. Virtual Env
Set up a virtual environment in this directory

`python -m venv venv`

Activate your virtualevn. This allows all packages installed in step 2 to be dedicated to this virtual workspace.

`.\venv\Scripts\activate.bat`

To deactivate your virtualenv

`deactivate`

## 2. Install Necessary Packages
Install all current package requirements

`python -m pip install -r requirements.txt`