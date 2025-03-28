"""
File operations for the Mod Side Checker.
"""
import os
import json
from colorama import Fore
from .utils import ColorPrinter


class FileManager:
    """Class for managing file operations."""
    
    # Define folder paths
    INPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "input")
    OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    
    @classmethod
    def ensure_folders_exist(cls):
        """Ensure input and output folders exist."""
        os.makedirs(cls.INPUT_FOLDER, exist_ok=True)
        os.makedirs(cls.OUTPUT_FOLDER, exist_ok=True)
        ColorPrinter.print(f"Input folder: {os.path.abspath(cls.INPUT_FOLDER)}", Fore.CYAN)
        ColorPrinter.print(f"Output folder: {os.path.abspath(cls.OUTPUT_FOLDER)}", Fore.CYAN)
    
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
