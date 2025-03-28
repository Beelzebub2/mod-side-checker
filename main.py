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

        # Create progress bars with better colors and fixed width
        progress_bars = []
        for i, batch in enumerate(mod_batches):
            progress_bars.append(
                tqdm(
                    total=len(batch),
                    desc=f"Thread {i+1:<2}",
                    position=i,
                    leave=True,
                    ncols=80,  # Fixed width
                    ascii=True,  # Use ASCII characters for better compatibility
                )
            )
        
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
                batch_results = future.result()
                results.extend(batch_results)
        
        # Close all progress bars
        for bar in progress_bars:
            bar.close()
        
        # Move cursor to bottom of progress bars
        print("\n" * (max_threads + 1))
        
        return pd.DataFrame(results) if results else None

    @staticmethod
    def save_filtered_list(mods_df, filter_type="all"):
            }
            
            for future in as_completed(future_to_batch):
                batch_results = future.result()
                results.extend(batch_results)
        
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
        gradient_success = ''.join(gradient_text(f"✓ Saved {len(mods_filtered)} mods to {filename}", (50, 255, 50), (0, 200, 0)))
        print(f"\n{gradient_success}")
        gradient_path = ''.join(gradient_text(f"File saved at: {os.path.abspath(filename)}", (147, 88, 254), (68, 166, 247)))
        print(gradient_path)

def print_header():
    ascii_art = """

███╗   ███╗ ██████╗ ██████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
████╗ ████║██╔═══██╗██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██╔████╔██║██║   ██║██║  ██║    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║╚██╔╝██║██║   ██║██║  ██║    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║ ╚═╝ ██║╚██████╔╝██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚═╝     ╚═╝ ╚═════╝ ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                        
    """
    print(''.join(gradient_text(ascii_art, (147, 88, 254), (68, 166, 247))))

def clean_exit(sig=None, frame=None):
    print_gradient("\n⚠️  Caught interrupt signal. Cleaning up...", (255, 165, 0), (255, 69, 0))
    print_gradient("✓ Cleanup complete. Goodbye!", (50, 255, 50), (0, 200, 0))
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, clean_exit)
    
    try:
        print_header()
        
        # Initialize ModChecker
        checker = ModChecker()
        print_gradient("\nLoading mod data...", (147, 88, 254), (68, 166, 247))
        total_mods = checker.load_data()
        
        # Get thread count
        while True:
            try:
                print_gradient("\n╭─── Thread Configuration ────╮", (147, 88, 254), (68, 166, 247))
                max_threads = int(input(''.join(gradient_text("│ Number of threads (1-10): ", (147, 88, 254), (68, 166, 247)))))
                if 1 <= max_threads <= 10:
                    print_gradient("╰──────────────────────────╯", (147, 88, 254), (68, 166, 247))
                    break
                print_gradient("→ Please enter a number between 1 and 10", (255, 69, 0), (255, 165, 0))
            except ValueError:
                print_gradient("→ Please enter a valid number", (255, 69, 0), (255, 165, 0))
        
        print_gradient(f"\nAnalyzing {total_mods} mods using {max_threads} threads...", (147, 88, 254), (68, 166, 247))
        mods_df = checker.process_mods(max_threads)
        
        if mods_df is not None:
            print_gradient("\n╭─── Summary ───────────────╮", (147, 88, 254), (68, 166, 247))
            print_gradient(f"│ Total mods: {len(mods_df)}", (147, 88, 254), (68, 166, 247))
            print_gradient("│ Distribution:", (147, 88, 254), (68, 166, 247))
            for side, count in mods_df['Side'].value_counts().items():
                print_gradient(f"│ • {side}: {count}", (147, 88, 254), (68, 166, 247))
            print_gradient("╰────────────────────────────╯", (147, 88, 254), (68, 166, 247))
            
            while True:
                print_gradient("\n╭─── Export Options ─────────╮", (147, 88, 254), (68, 166, 247))
                print_gradient("│ 1. Export all mods", (147, 88, 254), (68, 166, 247))
                print_gradient("│ 2. Export client-only mods", (147, 88, 254), (68, 166, 247))
                print_gradient("│ 3. Export server-only mods", (147, 88, 254), (68, 166, 247))
                print_gradient("│ 4. Export mods for both sides", (147, 88, 254), (68, 166, 247))
                print_gradient("│ 5. Export all types separately", (147, 88, 254), (68, 166, 247))
                print_gradient("│ 6. Exit", (147, 88, 254), (68, 166, 247))
                print_gradient("╰────────────────────────────╯", (147, 88, 254), (68, 166, 247))
                
                choice = input(''.join(gradient_text("\nEnter your choice (1-6): ", (147, 88, 254), (68, 166, 247))))
                
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
                    print_gradient("\nGoodbye!", (50, 255, 50), (0, 200, 0))
                    break
                else:
                    print_gradient("\nInvalid choice. Please try again.", (255, 69, 0), (255, 165, 0))
        else:
            print_gradient("No mod data found to process.", (255, 69, 0), (255, 165, 0))
    
    except Exception as e:
        print_gradient(f"\nError: {e}", (255, 69, 0), (255, 165, 0))
        clean_exit()

if __name__ == "__main__":
    main()
