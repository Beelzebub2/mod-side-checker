"""
File operations for the Mod Side Checker.
"""
import os
import json
import shutil
import zipfile
import tempfile
from colorama import Fore
from .utils import ColorPrinter


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
        
        # Create a new zip file
        with zipfile.ZipFile(output_path, 'w') as zip_out:
            # Add mods to the zip file
            for _, mod in mods_filtered.iterrows():
                download_url = mod['Download URL']
                mod_name = mod['Name']
                
                # Check if the mod file exists in the temp folder
                mod_path = os.path.join(cls.TEMP_FOLDER, 'overrides', 'mods', mod_name)
                if os.path.exists(mod_path):
                    # Use the local file
                    ColorPrinter.print(f"Adding mod from local file: {mod_name}", Fore.GREEN)
                    zip_out.write(mod_path, f"mods/{mod_name}")
                else:
                    # Just add mod info to the zip
                    info_text = f"Mod: {mod_name}\nSide: {mod['Side']}\nURL: {download_url}\n"
                    zip_out.writestr(f"mods_info/{mod_name}.txt", info_text)
        
        ColorPrinter.print(f"✓ Created {pack_type}-side modpack: {output_filename}", Fore.GREEN)
        ColorPrinter.print(f"File saved at: {os.path.abspath(output_path)}", Fore.CYAN)
        
        return output_path
