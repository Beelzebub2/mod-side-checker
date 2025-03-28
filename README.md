# Mod Side Checker

A tool to analyze Minecraft mod requirements for client and server environments.

## Features

- Multi-threaded mod analysis
- Progress visualization with color indicators
- Supports sorting mods by environment requirements
- Exports results to CSV files

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your `modrinth.index.json` file in the same directory as `main.py`
2. Run the script:
```bash
python main.py
```
3. Choose number of threads (1-10)
4. Wait for analysis to complete
5. Select export option from the menu

## How it Works

### Technical Overview

1. **Data Loading**: 
   - Reads mod data from modrinth.index.json
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

- `Lista_Mods_Com_Ambiente.csv`: All mods with their environment info
- `Lista_Mods_Client.csv`: Client-only mods
- `Lista_Mods_Server.csv`: Server-only mods
- `Lista_Mods_Both.csv`: Mods required on both sides

## License

MIT License
