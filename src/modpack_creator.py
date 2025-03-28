"""
Modpack creator functionality for creating server/client modpacks.
"""
import os
import shutil
import zipfile
import time
from colorama import Fore

# Try relative import first, fall back to absolute import if needed
try:
    from .utils import ColorPrinter
    from .file_manager import FileManager
    from .checker import ModChecker
except ImportError:
    import sys
    import os.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.utils import ColorPrinter
    from src.file_manager import FileManager
    from src.checker import ModChecker


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
            
            # First check if the mods directory exists
            mods_dir = os.path.join(FileManager.TEMP_FOLDER, 'mods')
            if not os.path.exists(mods_dir) or not os.listdir(mods_dir):
                ColorPrinter.print("Warning: No mod files found in the extracted modpack.", Fore.YELLOW)
                ColorPrinter.print("The pack will be created with info but may not contain actual mod files.", Fore.YELLOW)
            else:
                jar_count = len([f for f in os.listdir(mods_dir) if f.endswith('.jar')])
                ColorPrinter.print(f"Found {jar_count} mod JAR files for packaging", Fore.GREEN)
            
            # Process mods to determine sides
            ColorPrinter.print(f"\nAnalyzing {total_mods} mods using {thread_count} threads...", Fore.CYAN)
            mods_df = self.checker.process_mods(thread_count)
            
            if mods_df is None or mods_df.empty:
                ColorPrinter.print("No mod data available after processing.", Fore.RED)
                return False
            
            # Create summary of mod sides with a smaller top margin
            print("")  # Just one newline instead of multiple
            ColorPrinter.print("╭─── Modpack Analysis ────────╮", Fore.CYAN)
            ColorPrinter.print(f"│ Total mods: {len(mods_df)}", Fore.CYAN)
            side_counts = mods_df['Side'].value_counts()
            for side, count in side_counts.items():
                ColorPrinter.print(f"│ • {side}: {count}", Fore.CYAN)
            ColorPrinter.print("╰────────────────────────────╯", Fore.CYAN)
            
            # Create modpack based on type
            all_missing_mods = set()  # Track all missing mods
            
            if pack_type == 'server' or pack_type == 'both':
                output_path = FileManager.create_modpack_zip(mods_df, 'server')
                # Get missing mods from the output path (check for _missing_mods.txt file)
                missing_mods_path = os.path.join(FileManager.OUTPUT_FOLDER, "server_missing_mods.txt")
                if os.path.exists(missing_mods_path):
                    with open(missing_mods_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                mod_name = line.split(' - ')[0].strip()
                                all_missing_mods.add(mod_name)
                
            if pack_type == 'client' or pack_type == 'both':
                output_path = FileManager.create_modpack_zip(mods_df, 'client')
                # Get missing mods from the output path
                missing_mods_path = os.path.join(FileManager.OUTPUT_FOLDER, "client_missing_mods.txt")
                if os.path.exists(missing_mods_path):
                    with open(missing_mods_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip() and not line.startswith('#'):
                                mod_name = line.split(' - ')[0].strip()
                                all_missing_mods.add(mod_name)
            
            # If creating both packs, create a combined missing mods file
            if pack_type == 'both' and all_missing_mods:
                combined_missing_path = os.path.join(FileManager.OUTPUT_FOLDER, "all_missing_mods.txt")
                with open(combined_missing_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Missing Mods for ALL MODPACKS\n")
                    f.write(f"# Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"# The following {len(all_missing_mods)} mods were not found locally and need to be downloaded manually:\n\n")
                    
                    for mod in sorted(all_missing_mods):
                        # Find the mod's download URL if available
                        mod_info = mods_df[mods_df['Name'] == mod]
                        if not mod_info.empty:
                            download_url = mod_info.iloc[0]['Download URL']
                            f.write(f"{mod} - {download_url}\n")
                        else:
                            f.write(f"{mod}\n")
                
                ColorPrinter.print(f"  Created combined list of {len(all_missing_mods)} missing mods: all_missing_mods.txt", Fore.YELLOW)
            
            # Clean up temporary files
            FileManager.clean_temp_folder()
            
            ColorPrinter.print("\n✓ Modpack creation completed successfully!", Fore.GREEN)
            return True
            
        except Exception as e:
            ColorPrinter.print(f"Error creating modpack: {e}", Fore.RED)
            return False
