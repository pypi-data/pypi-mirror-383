#!/usr/bin/env python3
"""
Quack Sound Script
Plays quack.mp3 when escape key is pressed using only built-in libraries.
"""

import subprocess
import sys

def play_sound():
    """Play the quack sound using built-in libraries."""
    if sys.platform == "darwin":  # macOS
        subprocess.run(["afplay", "quack.mp3"], check=False)
    elif sys.platform == "win32":  # Windows
        subprocess.run(["powershell", "-c", "(New-Object Media.SoundPlayer 'quack.mp3').PlaySync()"], check=False)
    else:  # Linux
        subprocess.run(["aplay", "quack.mp3"], check=False)
    print("🦆 QUACK!")

def main():
    """Main function to detect key presses."""
    print("🦆 Quack Script Started!")
    print("Press ESC to quack, Ctrl+C to exit")
    
    if sys.platform == "win32":
        # Windows version using msvcrt (inspired by Stack Overflow)
        import msvcrt
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\x1b':  # ESC key
                    play_sound()
    else:
        # Unix/macOS version using termios
        import termios
        import tty
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            while True:
                key = sys.stdin.read(1)
                if key == '\x1b':  # ESC key
                    play_sound()
                elif key == '\x03':  # Ctrl+C
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
