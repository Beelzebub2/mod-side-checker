"""
Mod Side Checker - Main entry point.
Analyzes Minecraft mods to determine if they are client-side or server-side.
"""
import signal
import sys
import os

# Add the project root to the Python path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from colorama import Fore

from src.utils import ColorPrinter, SignalHandler
from src.ui import UserInterface
from src.file_manager import FileManager
from src.checker import ModChecker
from src.modpack_creator import ModpackCreator


class Application:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.checker = ModChecker()
        self.modpack_creator = ModpackCreator()
    
    def run_mod_checker(self):
        """Run the mod side checker functionality."""
        try:
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
                        ColorPrinter.print("\nReturning to main menu...", Fore.GREEN)
                        break
            else:
                ColorPrinter.print("No mod data found to process or operation was interrupted.", Fore.YELLOW)
        
        except Exception as e:
            ColorPrinter.print(f"\nError: {e}", Fore.RED)
    
    def run_modpack_creator(self):
        """Run the modpack creator functionality."""
        try:
            # Get thread count from user
            max_threads = UserInterface.get_thread_count()
            
            while True:
                # Get modpack choice
                choice = UserInterface.get_modpack_choice()
                
                if choice == '1':
                    # Create server-side pack
                    self.modpack_creator.create_modpack('server', max_threads)
                elif choice == '2':
                    # Create client-side pack
                    self.modpack_creator.create_modpack('client', max_threads)
                elif choice == '3':
                    # Create both packs
                    self.modpack_creator.create_modpack('both', max_threads)
                elif choice == '4':
                    ColorPrinter.print("\nReturning to main menu...", Fore.GREEN)
                    break
        
        except Exception as e:
            ColorPrinter.print(f"\nError: {e}", Fore.RED)
    
    def run(self):
        """Run the application."""
        try:
            # Display header
            UserInterface.print_header()
            
            while True:
                # Get application mode
                mode = UserInterface.get_application_mode()
                
                if mode == '1':
                    # Run mod checker
                    self.run_mod_checker()
                elif mode == '2':
                    # Run modpack creator
                    self.run_modpack_creator()
                
                # Ask if the user wants to exit
                ColorPrinter.print("\nReturn to the main menu? (y/n): ", Fore.CYAN, end='')
                if input().lower() != 'y':
                    ColorPrinter.print("\nGoodbye!", Fore.GREEN)
                    break
        
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
