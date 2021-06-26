# linuxcnc-streamdeck
Example of Elgato Stream Deck control of LinuxCNC

## Startup Steps
1. Start LinuxCNC
2. Start linuxcnc-server.py (IPC bridge between LinuxCNC and linuxcnc-streamdeck)
3. Start linuxcnc-streamdeck.py (Configures, reads, and maintains the Stream Deck)

## Additional
The distributed LinuxCNC 2.8 is built against an obsolete version of Python, which causes problems when trying to use both the LinuxCNC Python module and modules that have been updated to use Python 3. To work around the old Python version for the demo, I use a small IPC bridge. The linuxcnc-server must be started first which configures two named pipes. Then linuxcnc-streamdeck.py can be started.

## Hardware
Elgato Stream Deck [Amazon affiliate link](https://amzn.to/3h16lJ6)

## Warning
Because jog commands are sent to LinuxCNC as 'start' and 'stop' and there is no guarantee of receipt fromthe Stream Deck software, no watchdogs, etc., this code should only be seen as a proof of concept and not used in production without additional safety checks.
