# linuxcnc-streamdeck
Elgato StreamDeck control of LinuxCNC example

linuxcnc-streamdeck.py - Configures, reads, and maintains the Stream Deck

The distributed LinuxCNC 2.8 is built against an obsolete version of Python, which causes problems when trying to use both the LinuxCNC Python module and modules that have been updated to use Python 3. To work around the old Python version for the demo, I use a small IPC bridge. The linuxcnc-server must be started first which configures two named pipes. Then linuxcnc-streamdeck.py can be started.

client.py - IPC test program when can't use Stream Deck
linuxcnc-server.py - IPC bridge to LinuxCNC
test-server.py - IPC test program when can't use LinuxCNC

