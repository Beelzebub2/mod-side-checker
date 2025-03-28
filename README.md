# 🧩 Mod Side Checker

<div align="center">
  
![Mod Side Checker Banner](https://i.imgur.com/QJcyBTk.png)

*Quickly determine if your Minecraft mods are client-side, server-side, or both*

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Made for Modrinth](https://img.shields.io/badge/Made%20for-Modrinth-1bd96a)](https://modrinth.com)

</div>

## ✨ Overview

Mod Side Checker is a powerful tool that analyzes your Minecraft mod folder and tells you which mods need to be installed on the client, server, or both. Perfect for server administrators and modpack creators who want to optimize their mod distribution.

## 📥 Installation

1. Clone this repository or download the latest release
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the tool with:
   ```bash
   python -m src.main
   ```

## 🚀 Usage

1. Launch the tool
2. Select your mods folder or drag and drop a MultiMC/Prism instance
3. Wait for the analysis to complete
4. View the results, sorted by requirement type

## ⚙️ Configuration

The tool can be customized through the `config.json` file which is created on first run.

### API Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `user_agent` | User agent sent with API requests | `ModEnvironmentChecker/1.0` |
| `request_delay` | Delay between API requests (seconds) | `0.5` |

### UI Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `progress_bar_width` | Width of progress bars in characters | `80` |
| `use_ascii_bars` | Use ASCII characters for progress bars instead of blocks | `true` |
| `theme` | Color theme (options: "modrinth", "dark", "light") | `"modrinth"` |

### Export Configuration

| Option | Description | Default |
|--------|-------------|---------|
| `default_format` | Default export format (csv, json, markdown) | `"csv"` |
| `auto_export` | Automatically export results after scan | `false` |
| `export_path` | Default path for exported files | `"./exports"` |

## 🔍 Features

- **Multi-threaded Processing**: Analyzes all mods simultaneously for faster results
- **Visual Progress Tracking**: Color-coded progress bars show completion status
- **Modrinth API Integration**: Fetches accurate environment requirements
- **Export Options**: Save results as CSV, JSON, or markdown
- **Smart Detection**: Automatically identifies mod folders from popular launchers
- **Configurable**: Customize colors, performance, and more  

## 🔄 Example Output

```
CLIENT-SIDE ONLY (15 mods):
- 3D Skin Layers
- Animatica
- Better Third Person
- Iris Shaders
- Mod Menu

SERVER-SIDE ONLY (3 mods):
- Carpet
- Lithium
- ServerCore

BOTH SIDES REQUIRED (12 mods):
- Create
- Fabric API
- Origins
- Terralith
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💚 Acknowledgements

- [Modrinth](https://modrinth.com) for their amazing API
- All mod creators for their incredible work
