# linuxcnc-streamdeck
Example of Elgato Stream Deck control of LinuxCNC

## Startup Steps
1. Start LinuxCNC
2. Start linuxcnc-streamdeck.py (Configures, reads, and maintains the Stream Deck)

## Additional
This code branch is only for LinuxCNC 2.9 built against Python 3. The distributed LinuxCNC 2.8 is built against Python 2.7, and requires the IPC branch version to be used.

## Hardware
Elgato Stream Deck [Amazon affiliate link](https://amzn.to/3h16lJ6)

## Warning
Because jog commands are sent to LinuxCNC as 'start' and 'stop' and there is no guarantee of receipt from the Stream Deck software, no watchdogs, etc., this code should only be seen as a proof of concept and not used in production without additional safety checks.
