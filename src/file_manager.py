"""
File operations for the Mod Side Checker.
"""
import os
import json
import shutil
import zipfile
import tempfile
import time
from colorama import Fore

# Try relative import first, fall back to absolute import if needed
try:
    from .utils import ColorPrinter
except ImportError:
    import sys
    import os.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.utils import ColorPrinter


class FileManager:
    """Class for managing file operations."""
    
    # Define folder paths
    INPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input")
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    TEMP_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    
    @classmethod
    def ensure_folders_exist(cls):
        """Ensure input and output folders exist."""
        os.makedirs(cls.INPUT_FOLDER, exist_ok=True)
        os.makedirs(cls.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(cls.TEMP_FOLDER, exist_ok=True)
        ColorPrinter.print(f"Input folder: {os.path.abspath(cls.INPUT_FOLDER)}", Fore.CYAN)
        ColorPrinter.print(f"Output folder: {os.path.abspath(cls.OUTPUT_FOLDER)}", Fore.CYAN)
    
    @classmethod
    def clean_temp_folder(cls):
        """Clean up temporary folder."""
        if os.path.exists(cls.TEMP_FOLDER):
            shutil.rmtree(cls.TEMP_FOLDER)
            os.makedirs(cls.TEMP_FOLDER, exist_ok=True)
    
    @classmethod
    def extract_mrpack(cls, mrpack_file):
        """
        Extract a .mrpack file to the temp folder.
        
        Args:
            mrpack_file (str): Path to the .mrpack file
            
        Returns:
            str: Path to the extracted modrinth.index.json file
        """
        cls.clean_temp_folder()
        
        try:
            # Extract the .mrpack file (it's a zip file)
            with zipfile.ZipFile(mrpack_file, 'r') as zip_ref:
                zip_ref.extractall(cls.TEMP_FOLDER)
            
            # Path to the extracted modrinth.index.json
            json_path = os.path.join(cls.TEMP_FOLDER, 'modrinth.index.json')
            
            if not os.path.exists(json_path):
                ColorPrinter.print(f"modrinth.index.json not found in the .mrpack file!", Fore.RED)
                return None
            
            # Look for mods.zip in the overrides folder
            overrides_dir = os.path.join(cls.TEMP_FOLDER, 'overrides')
            if os.path.exists(overrides_dir):
                mods_zip = os.path.join(overrides_dir, 'mods.zip')
                mods_dir = os.path.join(cls.TEMP_FOLDER, 'mods')  # Use a direct mods folder for easier access
                
                # Create mods directory if it doesn't exist
                os.makedirs(mods_dir, exist_ok=True)
                
                # Check if mods.zip exists and extract it
                if os.path.exists(mods_zip):
                    ColorPrinter.print(f"Found mods.zip, extracting mod files...", Fore.GREEN)
                    try:
                        with zipfile.ZipFile(mods_zip, 'r') as zip_ref:
                            # Extract all files from mods.zip
                            for zip_info in zip_ref.infolist():
                                # Extract to root mods directory regardless of internal structure
                                if zip_info.filename.endswith('.jar'):
                                    # Get just the filename part (remove paths)
                                    jar_name = os.path.basename(zip_info.filename)
                                    
                                    # Extract to our mods directory
                                    source = zip_ref.open(zip_info)
                                    target = open(os.path.join(mods_dir, jar_name), "wb")
                                    with source, target:
                                        shutil.copyfileobj(source, target)
                                    
                        mod_count = len([f for f in os.listdir(mods_dir) if f.endswith('.jar')])
                        ColorPrinter.print(f"✓ Extracted {mod_count} mod files", Fore.GREEN)
                    except Exception as e:
                        ColorPrinter.print(f"Error extracting mods.zip: {e}", Fore.RED)
                else:
                    # Check if there's already a mods folder with jars
                    mods_in_overrides = os.path.join(overrides_dir, 'mods')
                    if os.path.exists(mods_in_overrides):
                        # Copy all jar files from the overrides/mods to our mods directory
                        jar_count = 0
                        for file in os.listdir(mods_in_overrides):
                            if file.endswith('.jar'):
                                shutil.copy2(
                                    os.path.join(mods_in_overrides, file),
                                    os.path.join(mods_dir, file)
                                )
                                jar_count += 1
                        
                        if jar_count > 0:
                            ColorPrinter.print(f"✓ Found and copied {jar_count} mod files from overrides/mods", Fore.GREEN)
            
            return json_path
        
        except Exception as e:
            ColorPrinter.print(f"Error extracting .mrpack file: {e}", Fore.RED)
            return None
    
    @classmethod
    def find_mrpack_file(cls):
        """
        Find a .mrpack file in the input folder.
        
        Returns:
            str: Path to the .mrpack file or None if not found
        """
        cls.ensure_folders_exist()
        
        for filename in os.listdir(cls.INPUT_FOLDER):
            if filename.endswith(".mrpack"):
                return os.path.join(cls.INPUT_FOLDER, filename)
        
        ColorPrinter.print("No .mrpack file found in the input folder!", Fore.RED)
        ColorPrinter.print(f"Please place a .mrpack file in: {os.path.abspath(cls.INPUT_FOLDER)}", Fore.YELLOW)
        return None
    
    @classmethod
    def load_mod_data(cls, filename="modrinth.index.json"):
        """
        Load mod data from the JSON file in input folder.
        
        Args:
            filename (str): Name of the JSON file.
            
        Returns:
            tuple: (data_dict, total_mods)
        """
        # Make sure folders exist
        cls.ensure_folders_exist()
        
        # First, check if we have a .mrpack file and try to extract it
        mrpack_path = cls.find_mrpack_file()
        if mrpack_path:
            ColorPrinter.print(f"Found .mrpack file: {os.path.basename(mrpack_path)}", Fore.GREEN)
            json_path = cls.extract_mrpack(mrpack_path)
            if json_path:
                ColorPrinter.print(f"Extracted modrinth.index.json from .mrpack", Fore.GREEN)
                # Copy the file to the input folder for future use
                shutil.copy(json_path, os.path.join(cls.INPUT_FOLDER, filename))
        
        # Look for the file in input folder
        json_path = os.path.join(cls.INPUT_FOLDER, filename)
        
        if not os.path.exists(json_path):
            ColorPrinter.print(f"File {filename} not found in input folder!", Fore.RED)
            ColorPrinter.print(f"Please place your {filename} file in: {os.path.abspath(cls.INPUT_FOLDER)}", Fore.YELLOW)
            return None, 0
        
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        total_mods = len(data.get('files', []))
        ColorPrinter.print(f"Found {total_mods} mods to process", Fore.CYAN)
        
        return data, total_mods
    
    @classmethod
    def save_filtered_list(cls, mods_df, filter_type="all"):
        """
        Save filtered mod list to CSV with accurate counting in output folder.
        
        Args:
            mods_df (DataFrame): Pandas DataFrame with mod data.
            filter_type (str): Type of filtering to apply.
        """
        if filter_type == "all":
            filename = "Lista_Mods_Com_Ambiente.csv"
            mods_filtered = mods_df
        elif filter_type == "client":
            filename = "Lista_Mods_Client.csv"
            # Only include strictly client-side mods
            mods_filtered = mods_df[mods_df['Side'] == 'Client']
        elif filter_type == "server":
            filename = "Lista_Mods_Server.csv"
            # Only include strictly server-side mods
            mods_filtered = mods_df[mods_df['Side'] == 'Server']
        elif filter_type == "both":
            filename = "Lista_Mods_Both.csv"
            # Only include mods that work on both sides
            mods_filtered = mods_df[mods_df['Side'] == 'Both']
        
        # Use output folder for saving files
        output_path = os.path.join(cls.OUTPUT_FOLDER, filename)
        
        # Save with proper encoding
        mods_filtered.to_csv(output_path, index=False, encoding='utf-8')
        ColorPrinter.print(f"✓ Saved {len(mods_filtered)} mods to {filename}", Fore.GREEN)
        ColorPrinter.print(f"File saved at: {os.path.abspath(output_path)}", Fore.CYAN)
    
    @classmethod
    def create_modpack_zip(cls, mods_df, pack_type):
        """
        Create a server-side or client-side modpack zip.
        
        Args:
            mods_df (DataFrame): DataFrame with mod data
            pack_type (str): Type of pack to create ('server' or 'client')
            
        Returns:
            str: Path to the created zip file
        """
        # Create the filtered dataframe based on pack type
        if pack_type == 'server':
            # Server pack needs Server and Both sides mods
            mods_filtered = mods_df[mods_df['Side'].isin(['Server', 'Both'])]
            output_filename = "server_pack.zip"
            ColorPrinter.print(f"Creating server-side modpack with {len(mods_filtered)} mods...", Fore.CYAN)
        else:  # client
            # Client pack needs Client and Both sides mods
            mods_filtered = mods_df[mods_df['Side'].isin(['Client', 'Both'])]
            output_filename = "client_pack.zip"
            ColorPrinter.print(f"Creating client-side modpack with {len(mods_filtered)} mods...", Fore.CYAN)
        
        # Path to the output zip file
        output_path = os.path.join(cls.OUTPUT_FOLDER, output_filename)
        
        # Path to the extracted mods directory
        mods_dir = os.path.join(cls.TEMP_FOLDER, 'mods')
        
        # Track which mods were found and included
        included_mods = []
        missing_mods = []
        
        # Create a temporary directory for organizing the pack
        pack_temp_dir = os.path.join(cls.TEMP_FOLDER, f"{pack_type}_pack")
        pack_mods_dir = os.path.join(pack_temp_dir, "mods")
        os.makedirs(pack_mods_dir, exist_ok=True)
        
        # Copy the appropriate mods
        if os.path.exists(mods_dir):
            for _, mod_row in mods_filtered.iterrows():
                mod_name = mod_row['Name']
                
                # Try different ways the mod might be named in the extracted files
                possible_filenames = [
                    mod_name,  # Exact name from index
                    mod_name.lower(),  # Lowercase variant
                ]
                
                # Also add any jar files that start with the mod name (without version)
                mod_base_name = mod_name.split('-')[0] if '-' in mod_name else mod_name.split('.jar')[0]
                
                found = False
                for jar_file in os.listdir(mods_dir):
                    # Check for exact matches
                    if jar_file in possible_filenames:
                        shutil.copy2(os.path.join(mods_dir, jar_file), os.path.join(pack_mods_dir, jar_file))
                        included_mods.append(jar_file)
                        found = True
                        break
                    # Check for files that start with the mod_base_name
                    elif jar_file.startswith(mod_base_name) and jar_file.endswith('.jar'):
                        shutil.copy2(os.path.join(mods_dir, jar_file), os.path.join(pack_mods_dir, jar_file))
                        included_mods.append(jar_file)
                        found = True
                        break
                
                if not found:
                    missing_mods.append(mod_name)
        
        # Create a report file
        report_path = os.path.join(pack_temp_dir, "modpack_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"{pack_type.upper()}-SIDE MODPACK REPORT\n")
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total mods included: {len(included_mods)}\n")
            f.write(f"Mods not found: {len(missing_mods)}\n\n")
            
            f.write("Side requirements:\n")
            for side, count in mods_filtered['Side'].value_counts().items():
                f.write(f"- {side}: {count}\n")
            
            f.write("\nINCLUDED MODS:\n")
            for mod in included_mods:
                f.write(f"- {mod}\n")
            
            if missing_mods:
                f.write("\nMISSING MODS:\n")
                for mod in missing_mods:
                    f.write(f"- {mod}\n")
        
        # Create a README file
        readme_path = os.path.join(pack_temp_dir, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# {pack_type.title()}-Side Modpack\n\n")
            f.write(f"This modpack was automatically generated by the Mod Side Checker tool.\n")
            f.write(f"It contains {len(included_mods)} mods that are required for the {pack_type} side.\n\n")
            
            f.write("## Installation\n\n")
            f.write("1. Extract the contents of this ZIP file\n")
            f.write(f"2. Place the mods folder in your Minecraft {pack_type} directory\n\n")
            
            f.write("## Side Requirements\n\n")
            f.write("This pack includes the following mod types:\n")
            f.write("- Both sides: Mods required on both client and server\n")
            f.write(f"- {pack_type.title()}-only: Mods that only need to be installed on the {pack_type}\n")
        
        # Create the final zip file
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            # Add all files from the pack_temp_dir
            for root, _, files in os.walk(pack_temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Add the file with appropriate internal path
                    arcname = os.path.relpath(file_path, pack_temp_dir)
                    zip_out.write(file_path, arcname)
        
        # Print results
        if included_mods:
            ColorPrinter.print(f"✓ Created {pack_type}-side modpack with {len(included_mods)} mods", Fore.GREEN)
        else:
            ColorPrinter.print(f"⚠ Created {pack_type}-side modpack with no mods (couldn't find any mod files)", Fore.YELLOW)
            
        if missing_mods:
            ColorPrinter.print(f"  Note: {len(missing_mods)} mods were not found locally", Fore.YELLOW)
            
        ColorPrinter.print(f"File saved at: {os.path.abspath(output_path)}", Fore.CYAN)
        
        return output_path
