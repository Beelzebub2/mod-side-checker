import json
import pandas as pd
import os
import requests
import time
from urllib.parse import urlparse
from colorama import init, Fore, Style
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import signal
import sys

# Initialize colorama
init()

def color_print(text, color=Fore.WHITE):
    """Print colored text using Colorama colors"""
    print(f"{color}{text}{Style.RESET_ALL}")

class ModChecker:
    def __init__(self):
        self.mods_data = []
        self.data = None
        self.progress_lock = Lock()
        self.processed_mods = set()  # Track processed mods to avoid duplicates
        
    def load_data(self):
        """Load and validate the mod data from JSON file"""
        json_path = os.path.join(os.path.dirname(__file__), 'modrinth.index.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        total_mods = len(self.data.get('files', []))
        color_print(f"Found {total_mods} mods to process", Fore.CYAN)
        return total_mods

    def get_mod_environment(self, download_url):
        """Get mod environment requirements from Modrinth API"""
        try:
            parts = download_url.split('/')
            project_id = next((parts[i + 1] for i, part in enumerate(parts) if part == 'data'), None)
            
            if not project_id:
                return "Unknown"
            
            headers = {
                "User-Agent": "ModEnvironmentChecker/1.0",
                "Accept": "application/json"
            }
            api_url = f"https://api.modrinth.com/v2/project/{project_id}"
            response = requests.get(api_url, headers=headers)
            time.sleep(0.5)
            
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
            color_print(f"Error fetching mod info for {download_url}: {e}", Fore.RED)
            return "Unknown"

    def process_mod_batch(self, mods_batch, thread_id, progress_bar):
        """Process a batch of mods assigned to a specific thread"""
        results = []
        for mod in mods_batch:
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
                color_print(f"Error processing mod {name}: {e}", Fore.RED)
        
        return results

    def update_progress_color(self, progress_bar, progress):
        """Update progress bar color based on completion percentage"""
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
        """Process mods using multiple threads with separate progress bars"""
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

        # Create progress bars with pip-style formatting and initial red color
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
                    ncols=80,
                    ascii=True,
                    bar_format=f'{initial_color}  {{desc}}: |{{bar}}| {{percentage:3.0f}}%{Style.RESET_ALL}',
                )
            )
            # Initialize with 0% progress color
            self.update_progress_color(progress_bars[-1], 0)

        # Create a clean exit handler for ctrl+c during processing
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        
        def processing_sigint_handler(sig, frame):
            # Close progress bars
            for bar in progress_bars:
                bar.close()
            # Print newlines to move cursor past progress bars
            print("\n" * (max_threads + 2))
            color_print("\n⚠️  Interrupted! Cleaning up threads...", Fore.YELLOW)
            color_print("✓ Cleanup complete. Exiting...", Fore.GREEN)
            sys.exit(1)
        
        # Set temporary handler during processing
        signal.signal(signal.SIGINT, processing_sigint_handler)
        
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
                
                for future in as_completed(future_to_batch):
                    try:
                        batch_results = future.result()
                        results.extend(batch_results)
                    except Exception as e:
                        color_print(f"Error in thread: {e}", Fore.RED)
        finally:
            # Restore original SIGINT handler
            signal.signal(signal.SIGINT, original_sigint_handler)
            
            # Close all progress bars
            for bar in progress_bars:
                bar.close()
            
            # Move cursor to bottom of progress bars
            print("\n" * (max_threads + 1))
        
        return pd.DataFrame(results) if results else None

    @staticmethod
    def save_filtered_list(mods_df, filter_type="all"):
        """Save filtered mod list to CSV with accurate counting"""
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
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        # Save with proper encoding
        mods_filtered.to_csv(filename, index=False, encoding='utf-8')
        color_print(f"✓ Saved {len(mods_filtered)} mods to {filename}", Fore.GREEN)
        color_print(f"File saved at: {os.path.abspath(filename)}", Fore.CYAN)

def print_header():
    ascii_art = """
███╗   ███╗ ██████╗ ██████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
████╗ ████║██╔═══██╗██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██╔████╔██║██║   ██║██║  ██║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║╚██╔╝██║██║   ██║██║  ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║╚██████╔╝██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝ ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    """
    color_print(ascii_art, Fore.BLUE)

def clean_exit(sig=None, frame=None):
    color_print("\n⚠️  Caught interrupt signal. Cleaning up...", Fore.YELLOW)
    color_print("✓ Cleanup complete. Goodbye!", Fore.GREEN)
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, clean_exit)
    
    try:
        print_header()
        
        # Initialize ModChecker
        checker = ModChecker()
        color_print("\nLoading mod data...", Fore.CYAN)
        total_mods = checker.load_data()
        
        # Get thread count
        while True:
            try:
                color_print("\n╭─── Thread Configuration ────╮", Fore.CYAN)
                max_threads = int(input(f"{Fore.CYAN}│ Number of threads (1-10): {Style.RESET_ALL}"))
                if 1 <= max_threads <= 10:
                    color_print("╰──────────────────────────╯", Fore.CYAN)
                    break
                color_print("→ Please enter a number between 1 and 10", Fore.YELLOW)
            except ValueError:
                color_print("→ Please enter a valid number", Fore.YELLOW)
        
        color_print(f"\nAnalyzing {total_mods} mods using {max_threads} threads...", Fore.CYAN)
        # Temporarily disable the main SIGINT handler during processing
        old_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            mods_df = checker.process_mods(max_threads)
        finally:
            # Restore the main SIGINT handler
            signal.signal(signal.SIGINT, old_handler)
        
        if mods_df is not None:
            color_print("\n╭─── Summary ───────────────╮", Fore.CYAN)
            color_print(f"│ Total mods: {len(mods_df)}", Fore.CYAN)
            color_print("│ Distribution:", Fore.CYAN)
            for side, count in mods_df['Side'].value_counts().items():
                color_print(f"│ • {side}: {count}", Fore.CYAN)
            color_print("╰────────────────────────────╯", Fore.CYAN)
            
            while True:
                color_print("\n╭─── Export Options ─────────╮", Fore.CYAN)
                color_print("│ 1. Export all mods", Fore.CYAN)
                color_print("│ 2. Export client-only mods", Fore.CYAN)
                color_print("│ 3. Export server-only mods", Fore.CYAN)
                color_print("│ 4. Export mods for both sides", Fore.CYAN)
                color_print("│ 5. Export all types separately", Fore.CYAN)
                color_print("│ 6. Exit", Fore.CYAN)
                color_print("╰────────────────────────────╯", Fore.CYAN)
                
                choice = input(f"{Fore.CYAN}\nEnter your choice (1-6): {Style.RESET_ALL}")
                
                if choice == '1':
                    checker.save_filtered_list(mods_df, "all")
                elif choice == '2':
                    checker.save_filtered_list(mods_df, "client")
                elif choice == '3':
                    checker.save_filtered_list(mods_df, "server")
                elif choice == '4':
                    checker.save_filtered_list(mods_df, "both")
                elif choice == '5':
                    checker.save_filtered_list(mods_df, "all")
                    checker.save_filtered_list(mods_df, "client")
                    checker.save_filtered_list(mods_df, "server")
                    checker.save_filtered_list(mods_df, "both")
                elif choice == '6':
                    color_print("\nGoodbye!", Fore.GREEN)
                    break
                else:
                    color_print("\nInvalid choice. Please try again.", Fore.YELLOW)
        else:
            color_print("No mod data found to process.", Fore.YELLOW)
    
    except Exception as e:
        color_print(f"\nError: {e}", Fore.RED)
        clean_exit()

if __name__ == "__main__":
    main()
