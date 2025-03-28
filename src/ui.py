"""
User interface elements for the Mod Side Checker.
"""
from colorama import Fore, Style

# Try relative import first, fall back to absolute import if needed
try:
    from .utils import ColorPrinter
    from .config_manager import ConfigManager
except ImportError:
    import sys
    import os.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.utils import ColorPrinter
    from src.config_manager import ConfigManager


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
    def get_application_mode():
        """
        Get the application mode from user.
        
        Returns:
            str: Selected mode ('1' for Checker, '2' for Modpack Creator)
        """
        while True:
            ColorPrinter.print("\n╭─── Select Mode ─────────────╮", Fore.CYAN)
            ColorPrinter.print("│ 1. Mod Side Checker        │", Fore.CYAN)
            ColorPrinter.print("│ 2. Modpack Creator         │", Fore.CYAN)
            ColorPrinter.print("╰────────────────────────────╯", Fore.CYAN)
            
            choice = input(f"{Fore.CYAN}\nEnter your choice (1-2): {Style.RESET_ALL}")
            
            if choice in ["1", "2"]:
                return choice
            
            ColorPrinter.print("→ Please enter a valid option (1-2)", Fore.YELLOW)

    @staticmethod
    def get_thread_count():
        """
        Get the number of threads from user input.
        
        Returns:
            int: Number of threads to use
        """
        # Get thread limits from config
        max_allowed = ConfigManager.get('threading', 'max_threads', default=10)
        recommended_max = ConfigManager.get('threading', 'recommended_max', default=6)
        warning = ConfigManager.get('threading', 'warning', default='')
        
        while True:
            try:
                ColorPrinter.print("\n╭─── Thread Configuration ────╮", Fore.CYAN)
                ColorPrinter.print(f"│ Recommended max: {recommended_max}        │", Fore.CYAN)
                if warning:
                    ColorPrinter.print(f"│ {warning[:30]}... │", Fore.YELLOW)
                max_threads = int(input(f"{Fore.CYAN}│ Number of threads (1-{max_allowed}): {Style.RESET_ALL}"))
                if 1 <= max_threads <= max_allowed:
                    if max_threads > recommended_max:
                        ColorPrinter.print(f"│ Note: Using {max_threads} threads may affect UI stability", Fore.YELLOW)
                    ColorPrinter.print("╰──────────────────────────╯", Fore.CYAN)
                    return max_threads
                ColorPrinter.print(f"→ Please enter a number between 1 and {max_allowed}", Fore.YELLOW)
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

    @staticmethod
    def get_modpack_choice():
        """
        Get modpack creator option from user.
        
        Returns:
            str: User's choice ('1'-'4')
        """
        while True:
            ColorPrinter.print("\n╭─── Modpack Creator Options ───╮", Fore.CYAN)
            ColorPrinter.print("│ 1. Create server-side pack    │", Fore.CYAN)
            ColorPrinter.print("│ 2. Create client-side pack    │", Fore.CYAN)
            ColorPrinter.print("│ 3. Create both packs          │", Fore.CYAN)
            ColorPrinter.print("│ 4. Return to main menu        │", Fore.CYAN)
            ColorPrinter.print("╰────────────────────────────────╯", Fore.CYAN)
            
            choice = input(f"{Fore.CYAN}\nEnter your choice (1-4): {Style.RESET_ALL}")
            
            if choice in ["1", "2", "3", "4"]:
                return choice
            
            ColorPrinter.print("\nInvalid choice. Please try again.", Fore.YELLOW)
