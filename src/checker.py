"""
Core functionality for checking mod environments.
"""
import os
import time
import signal
import sys
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
from tqdm import tqdm
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


class ModChecker:
    """Class for checking mod environment requirements."""
    
    def __init__(self):
        """Initialize the ModChecker."""
        self.mods_data = []
        self.data = None
        self.progress_lock = Lock()
        self.processed_mods = set()  # Track processed mods to avoid duplicates
        self.stop_event = Event()  # Event to signal threads to stop
    
    def set_data(self, data):
        """
        Set the mod data.
        
        Args:
            data (dict): Mod data loaded from JSON
        """
        self.data = data
    
    def get_mod_environment(self, download_url):
        """
        Get mod environment requirements from Modrinth API.
        
        Args:
            download_url (str): Download URL for the mod.
            
        Returns:
            str: Environment type (Client, Server, Both, Optional, Unknown)
        """
        try:
            # Check if we should stop processing
            if self.stop_event.is_set():
                return "Unknown"
                
            parts = download_url.split('/')
            project_id = next((parts[i + 1] for i, part in enumerate(parts) if part == 'data'), None)
            
            if not project_id:
                return "Unknown"
            
            headers = {
                "User-Agent": ConfigManager.get('api', 'user_agent', default="ModEnvironmentChecker/1.0"),
                "Accept": "application/json"
            }
            api_url = f"https://api.modrinth.com/v2/project/{project_id}"
            response = requests.get(api_url, headers=headers)
            
            # Use request delay from config
            time.sleep(ConfigManager.get('api', 'request_delay', default=0.5))
            
            if response.status_code == 200:
                project_data = response.json()
                client_side = project_data.get('client_side', 'unknown')
                server_side = project_data.get('server_side', 'unknown')
                
                if client_side == "required" and server_side == "required":
                    return "Both"
                elif client_side == "required":
                    return "Client"
                elif server_side == "required":
                    return "Server"
                elif client_side == "optional" and server_side == "optional":
                    return "Optional"
                else:
                    return f"Client: {client_side}, Server: {server_side}"
            
            return "Unknown"
        except Exception as e:
            ColorPrinter.print(f"Error fetching mod info for {download_url}: {e}", Fore.RED)
            return "Unknown"
    
    def process_mod_batch(self, mods_batch, thread_id, progress_bar):
        """
        Process a batch of mods assigned to a specific thread.
        
        Args:
            mods_batch (list): List of mods to process.
            thread_id (int): Thread identifier.
            progress_bar (tqdm): Progress bar for this thread.
            
        Returns:
            list: List of processed mod data.
        """
        results = []
        for mod in mods_batch:
            # Check if we should stop processing
            if self.stop_event.is_set():
                break
                
            try:
                path = mod.get('path', '')
                name = os.path.basename(path) if path else "Unknown"
                
                # Skip if already processed
                if name in self.processed_mods:
                    continue
                
                download_links = mod.get('downloads', [])
                download_url = download_links[0] if download_links else ""
                side = self.get_mod_environment(download_url)
                
                with self.progress_lock:
                    self.processed_mods.add(name)
                    progress_bar.update(1)
                    # Update color based on progress
                    progress = progress_bar.n / progress_bar.total
                    self.update_progress_color(progress_bar, progress)
                    # Use fixed width for description to prevent size changes
                    progress_bar.set_description(f"Thread {thread_id:<2} {name[:20]:<20}")
                
                results.append({
                    'Name': name,
                    'Side': side,
                    'Download URL': download_url
                })
                
            except Exception as e:
                ColorPrinter.print(f"Error processing mod {name}: {e}", Fore.RED)
        
        return results
    
    def update_progress_color(self, progress_bar, progress):
        """
        Update progress bar color based on completion percentage.
        
        Args:
            progress_bar (tqdm): Progress bar to update.
            progress (float): Progress percentage (0.0 to 1.0).
        """
        # Calculate color: red (255,0,0) → yellow (255,255,0) → green (0,255,0)
        if progress < 0.5:
            # Red to yellow gradient (increase green)
            r = 255
            g = int(255 * progress * 2)  # 0 to 255 as progress goes 0 to 0.5
            b = 0
        else:
            # Yellow to green gradient (decrease red)
            r = int(255 * (1 - progress) * 2)  # 255 to 0 as progress goes 0.5 to 1
            g = 255
            b = 0
            
        # Format color code to ensure values are in valid range
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        # Set the color directly in the format string
        color_code = f"\033[38;2;{r};{g};{b}m"
        progress_bar.bar_format = f"{color_code}  {{desc}}: |{{bar}}| {{percentage:3.0f}}%{Style.RESET_ALL}"
    
    def process_mods(self, max_threads):
        """
        Process mods using multiple threads with separate progress bars.
        
        Args:
            max_threads (int): Number of threads to use.
            
        Returns:
            DataFrame: Pandas DataFrame with processed mod data.
        """
        # Reset stop event
        self.stop_event.clear()
        
        # We'll handle keyboard interrupts more directly at the executor level
        # rather than with a separate monitoring thread
        
        mods_list = self.data.get('files', [])
        total_mods = len(mods_list)
        
        # Split mods into batches for each thread
        batch_size = total_mods // max_threads
        mod_batches = [
            mods_list[i:i + batch_size] 
            for i in range(0, total_mods, batch_size)
        ]
        
        # Adjust last batch to include remaining mods
        if len(mod_batches) > max_threads:
            mod_batches[-2].extend(mod_batches[-1])
            mod_batches.pop()

        # Get UI settings from config
        progress_bar_width = ConfigManager.get('ui', 'progress_bar_width', default=80)
        use_ascii_bars = ConfigManager.get('ui', 'use_ascii_bars', default=True)
        
        # Create progress bars with settings from config
        progress_bars = []
        for i, batch in enumerate(mod_batches):
            # Start with red color
            initial_color = "\033[38;2;255;0;0m"  # Red
            progress_bars.append(
                tqdm(
                    total=len(batch),
                    desc=f"Thread {i+1:<2}",
                    position=i,
                    leave=True,
                    ncols=progress_bar_width,
                    ascii=use_ascii_bars,
                    bar_format=f'{initial_color}  {{desc}}: |{{bar}}| {{percentage:3.0f}}%{Style.RESET_ALL}',
                )
            )
            # Initialize with 0% progress color
            self.update_progress_color(progress_bars[-1], 0)

        # Variable to track if we were truly interrupted
        was_interrupted = False
        
        try:
            results = []
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                future_to_batch = {
                    executor.submit(
                        self.process_mod_batch, 
                        batch, 
                        i+1, 
                        progress_bars[i]
                    ): i 
                    for i, batch in enumerate(mod_batches)
                }
                
                # Wait for all tasks to complete
                for future in as_completed(future_to_batch):
                    try:
                        batch_results = future.result()
                        results.extend(batch_results)
                    except Exception as e:
                        ColorPrinter.print(f"Error in thread: {e}", Fore.RED)
        except KeyboardInterrupt:
            # This will catch actual keyboard interrupts
            was_interrupted = True
            ColorPrinter.print("\nKeyboard interrupt detected. Stopping processing...", Fore.YELLOW)
            self.stop_event.set()  # Signal all threads to stop at next opportunity
            # Don't re-raise the exception, let the cleanup proceed
        finally:
            # Clean up
            for bar in progress_bars:
                bar.close()
            
            # Move cursor to bottom of progress bars - reduce space
            print("\n" * (max_threads // 2 + 1))  # Reduced from (max_threads + 1)
            
            # Only show the interrupt message if it was actually interrupted by user
            if was_interrupted:
                ColorPrinter.print("Stopped due to user interrupt. Partial results available.", Fore.YELLOW)
        
        df = pd.DataFrame(results) if results else None
        
        # If we have results, even partial ones, return them
        return df
