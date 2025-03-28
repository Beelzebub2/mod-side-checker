"""
Utility functions for the Mod Side Checker.
"""
import sys
import signal
from colorama import init, Fore, Style

# Initialize colorama
init()

class ColorPrinter:
    """Class for printing colored text."""
    
    @staticmethod
    def print(text, color=Fore.WHITE, end='\n'):
        """
        Print colored text using Colorama colors.
        
        Args:
            text (str): Text to print
            color (colorama.Fore): Color to use
            end (str): String appended after the last value, default is newline
        """
        print(f"{color}{text}{Style.RESET_ALL}", end=end)


class SignalHandler:
    """Class for handling system signals."""
    
    @staticmethod
    def clean_exit(sig=None, frame=None):
        """
        Handle clean exit when interrupted.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        ColorPrinter.print("\n⚠️  Caught interrupt signal. Cleaning up...", Fore.YELLOW)
        ColorPrinter.print("✓ Cleanup complete. Goodbye!", Fore.GREEN)
        sys.exit(0)
    
    @staticmethod
    def setup_signal_handling():
        """Set up signal handlers for the application."""
        signal.signal(signal.SIGINT, SignalHandler.clean_exit)
