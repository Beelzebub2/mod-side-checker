"""
Mod Side Checker - Main entry point.
Analyzes Minecraft mods to determine if they are client-side or server-side.
"""
import signal
import sys

from colorama import Fore

from src.utils import ColorPrinter, SignalHandler
from src.ui import UserInterface
from src.file_manager import FileManager
from src.checker import ModChecker


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.checker = ModChecker()
    
    def run(self):
        """Run the application."""
        try:
            # Display header
            UserInterface.print_header()
            
            # Load mod data
            ColorPrinter.print("\nLoading mod data...", Fore.CYAN)
            data, total_mods = FileManager.load_mod_data()
            
            # Exit if no data was loaded
            if not data:
                ColorPrinter.print("Exiting due to missing input file.", Fore.RED)
                return
            
            self.checker.set_data(data)
            
            # Get thread count from user
            max_threads = UserInterface.get_thread_count()
            
            # Process mods
            ColorPrinter.print(f"\nAnalyzing {total_mods} mods using {max_threads} threads...", Fore.CYAN)
            
            # Process mods - the checker now handles keyboard interrupts internally
            mods_df = self.checker.process_mods(max_threads)
            
            # Display results and handle export options
            if mods_df is not None and not mods_df.empty:
                # Print summary
                UserInterface.print_summary(mods_df)
                
                # Export options
                while True:
                    choice = UserInterface.get_export_choice()
                    
                    if choice == '1':
                        FileManager.save_filtered_list(mods_df, "all")
                    elif choice == '2':
                        FileManager.save_filtered_list(mods_df, "client")
                    elif choice == '3':
                        FileManager.save_filtered_list(mods_df, "server")
                    elif choice == '4':
                        FileManager.save_filtered_list(mods_df, "both")
                    elif choice == '5':
                        FileManager.save_filtered_list(mods_df, "all")
                        FileManager.save_filtered_list(mods_df, "client")
                        FileManager.save_filtered_list(mods_df, "server")
                        FileManager.save_filtered_list(mods_df, "both")
                    elif choice == '6':
                        ColorPrinter.print("\nGoodbye!", Fore.GREEN)
                        break
            else:
                ColorPrinter.print("No mod data found to process or operation was interrupted.", Fore.YELLOW)
        
        except Exception as e:
            ColorPrinter.print(f"\nError: {e}", Fore.RED)
            SignalHandler.clean_exit()


def main():
    """Main entry point."""
    # Set up signal handler for clean exit
    SignalHandler.setup_signal_handling()
    
    # Create and run the application
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
