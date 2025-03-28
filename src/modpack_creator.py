"""
Modpack creator functionality for creating server/client modpacks.
"""
import os
import shutil
import zipfile
from colorama import Fore
from .utils import ColorPrinter
from .file_manager import FileManager
from .checker import ModChecker


class ModpackCreator:
    """Class for creating server/client modpacks."""
    
    def __init__(self):
        """Initialize the modpack creator."""
        self.checker = ModChecker()
    
    def create_modpack(self, pack_type, thread_count=4):
        """
        Create a modpack of the specified type.
        
        Args:
            pack_type (str): Type of pack to create ('server', 'client', or 'both')
            thread_count (int): Number of threads to use for processing
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load mod data from mrpack
            ColorPrinter.print("\nLooking for modpack files...", Fore.CYAN)
            data, total_mods = FileManager.load_mod_data()
            
            if not data:
                ColorPrinter.print("No modpack data found. Please add a .mrpack file to the input folder.", Fore.RED)
                return False
            
            # Set data for the checker
            self.checker.set_data(data)
            
            # Process mods to determine sides
            ColorPrinter.print(f"\nAnalyzing {total_mods} mods using {thread_count} threads...", Fore.CYAN)
            mods_df = self.checker.process_mods(thread_count)
            
            if mods_df is None or mods_df.empty:
                ColorPrinter.print("No mod data available after processing.", Fore.RED)
                return False
            
            # Create summary of mod sides
            ColorPrinter.print("\n╭─── Modpack Analysis ────────╮", Fore.CYAN)
            ColorPrinter.print(f"│ Total mods: {len(mods_df)}", Fore.CYAN)
            side_counts = mods_df['Side'].value_counts()
            for side, count in side_counts.items():
                ColorPrinter.print(f"│ • {side}: {count}", Fore.CYAN)
            ColorPrinter.print("╰────────────────────────────╯", Fore.CYAN)
            
            # Create modpack based on type
            if pack_type == 'server' or pack_type == 'both':
                FileManager.create_modpack_zip(mods_df, 'server')
                
            if pack_type == 'client' or pack_type == 'both':
                FileManager.create_modpack_zip(mods_df, 'client')
            
            # Clean up temporary files
            FileManager.clean_temp_folder()
            
            ColorPrinter.print("\n✓ Modpack creation completed successfully!", Fore.GREEN)
            return True
            
        except Exception as e:
            ColorPrinter.print(f"Error creating modpack: {e}", Fore.RED)
            return False
