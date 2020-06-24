# cmwb
A very lightweight work in progress browser written in python, and soon to support extensions!

# Installation
There are two ways to use cmwb. The first option is to install the dependencies manually and run it without installing. <br />
The second option is to make the installer executable and it will automatically install itself, it's dependencies, and make shortcuts. <br />
To make the installer executable run `chmod +x install.sh` in a terminal, once that completes successfully, run `./install.sh`. <br />
<br />
The installer can only complete on a linux machine with the apt package manager. We are working on releasing a Mac OS version that will use the homebrew package manager, and eventually a windows version that will use the winget package manager. <br />
<br />
# Dependencies
- python3 <br />
- pip3 <br />
- cefpython <br />
- tkinter <br />

# Open the Browser
If you chose the first option to install, you can start the browser by running `python3 browser.py`. <br />
If you chose the second option to install, you can start the browser by running the desktop or menu shortcut on your linux machine. <br />

# Future features
- Bookmarks <br />
- History Tracking <br />
- Python based extensions and APIs <br />
