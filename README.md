# Mod Side Checker & Modpack Creator

A tool to analyze Minecraft mod requirements for client and server environments and create customized modpacks.

## Features

- **Mod Analyzer**:
  - Multi-threaded mod analysis
  - Progress visualization with color indicators
  - Detailed side requirement reports
  - Exports results to CSV files

- **Modpack Creator**:
  - Creates server-side and client-side modpacks
  - Automatically separates mods based on side requirements
  - Works with .mrpack files

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Getting Started

1. Place either a `modrinth.index.json` file or a `.mrpack` file in the `input` folder
   - The program will create the folder if it doesn't exist
2. Run the script:
```bash
python main.py
```
3. Choose the mode (Mod Checker or Modpack Creator)
4. Follow the on-screen instructions

### Mod Side Checker

1. Select option 1 from the main menu
2. Choose number of threads (1-10)
3. Wait for analysis to complete
4. Select export option from the menu
5. Find exported CSV files in the `output` folder

### Modpack Creator

1. Select option 2 from the main menu
2. Choose number of threads (1-10)
3. Wait for analysis to complete
4. Select modpack type to create (server, client, or both)
5. Find created modpacks in the `output` folder

## How it Works

### Technical Overview

1. **Data Loading**: 
   - Reads mod data from input/modrinth.index.json or extracts it from .mrpack file
   - Validates file structure and content

2. **Multi-threading**:
   - Divides mods into equal batches
   - Each thread processes its batch independently
   - Uses thread-safe progress tracking

3. **API Integration**:
   - Queries Modrinth API for each mod
   - Analyzes client/server requirements
   - Implements rate limiting to avoid API overload

4. **Environment Categories**:
   - Client: Client-side only mods
   - Server: Server-side only mods
   - Both: Required on both sides
   - Optional: Optional on both sides

### Output Files

All files are saved to the `output` folder:

**CSV Files:**
- `Lista_Mods_Com_Ambiente.csv`: All mods with their environment info
- `Lista_Mods_Client.csv`: Client-only mods
- `Lista_Mods_Server.csv`: Server-only mods
- `Lista_Mods_Both.csv`: Mods required on both sides

**Modpack Files:**
- `server_pack.zip`: Modpack with server-side and shared mods
- `client_pack.zip`: Modpack with client-side and shared mods

## License

MIT License
