"""
User interface elements for the Mod Side Checker.
"""
from colorama import Fore, Style
from .utils import ColorPrinter


class UserInterface:
    """Class for user interface elements."""
    
    @staticmethod
    def print_header():
        """Print the application header."""
        ascii_art = """
███╗   ███╗ ██████╗ ██████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
████╗ ████║██╔═══██╗██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██╔████╔██║██║   ██║██║  ██║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║╚██╔╝██║██║   ██║██║  ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║╚██████╔╝██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝ ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
        """
        ColorPrinter.print(ascii_art, Fore.BLUE)

    @staticmethod
    def get_thread_count():
        """
        Get the number of threads from user input.
        
        Returns:
            int: Number of threads to use
        """
        while True:
            try:
                ColorPrinter.print("\n╭─── Thread Configuration ────╮", Fore.CYAN)
                max_threads = int(input(f"{Fore.CYAN}│ Number of threads (1-10): {Style.RESET_ALL}"))
                if 1 <= max_threads <= 10:
                    ColorPrinter.print("╰──────────────────────────╯", Fore.CYAN)
                    return max_threads
                ColorPrinter.print("→ Please enter a number between 1 and 10", Fore.YELLOW)
            except ValueError:
                ColorPrinter.print("→ Please enter a valid number", Fore.YELLOW)

    @staticmethod
    def print_summary(mods_df):
        """
        Print summary of mods analysis.
        
        Args:
            mods_df (DataFrame): DataFrame containing mod data
        """
        ColorPrinter.print("\n╭─── Summary ───────────────╮", Fore.CYAN)
        ColorPrinter.print(f"│ Total mods: {len(mods_df)}", Fore.CYAN)
        ColorPrinter.print("│ Distribution:", Fore.CYAN)
        for side, count in mods_df['Side'].value_counts().items():
            ColorPrinter.print(f"│ • {side}: {count}", Fore.CYAN)
        ColorPrinter.print("╰────────────────────────────╯", Fore.CYAN)

    @staticmethod
    def get_export_choice():
        """
        Get export option from user.
        
        Returns:
            str: User's choice ('1'-'6')
        """
        while True:
            ColorPrinter.print("\n╭─── Export Options ─────────╮", Fore.CYAN)
            ColorPrinter.print("│ 1. Export all mods", Fore.CYAN)
            ColorPrinter.print("│ 2. Export client-only mods", Fore.CYAN)
            ColorPrinter.print("│ 3. Export server-only mods", Fore.CYAN)
            ColorPrinter.print("│ 4. Export mods for both sides", Fore.CYAN)
            ColorPrinter.print("│ 5. Export all types separately", Fore.CYAN)
            ColorPrinter.print("│ 6. Exit", Fore.CYAN)
            ColorPrinter.print("╰────────────────────────────╯", Fore.CYAN)
            
            choice = input(f"{Fore.CYAN}\nEnter your choice (1-6): {Style.RESET_ALL}")
            
            if choice in ["1", "2", "3", "4", "5", "6"]:
                return choice
            
            ColorPrinter.print("\nInvalid choice. Please try again.", Fore.YELLOW)
