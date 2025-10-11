### pg_helpers/notifications.py
"""Notification utilities"""
import os
import sys

def play_notification_sound():
    """
    Play notification sound based on operating system
    """
    try:
        if sys.platform == "darwin":  # macOS
            os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        elif sys.platform == "win32":  # Windows
            try:
                import winsound
                winsound.PlaySound(r"C:\Windows\Media\tada.wav", winsound.SND_FILENAME)
            except ImportError:
                pass  # winsound not available
        # Linux/other systems - could add more sound options here
    except Exception:
        pass  # Silently fail if sound can't be played
