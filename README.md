# ForgeUI Quick Presets

A simple extension to save, load, and manage your Stable Diffusion prompt presets.

## Features

- **Save Presets**: Save your prompt, negative prompt, sampler, steps, CFG, and dimensions as a named preset
- **Load Presets**: Quickly load saved presets from a dropdown
- **Delete Presets**: Remove presets you no longer need
- **Import/Export**: Share presets with others via JSON
- **Dedicated Tab**: Full preset management interface in its own tab

## Installation

### Method 1: Clone (Recommended)

1. Open ForgeUI's `extensions` folder
2. Clone this repository:
   ```bash
   cd extensions
   git clone https://github.com/yourusername/forgeui-quick-presets.git
   ```
3. Restart ForgeUI

### Method 2: Download

1. Download this repository as a ZIP file
2. Extract to your ForgeUI `extensions` folder
3. Restart ForgeUI

## Usage

### From txt2img / img2img

1. Scroll down to find the "Quick Presets" accordion
2. To save: Enter a name and click "Save Preset"
3. To load: Select a preset from the dropdown
4. To delete: Select a preset and click "Delete"

### From the Presets Manager Tab

1. Go to the "Quick Presets" tab
2. View all saved presets in the table
3. Create new presets or edit existing ones
4. Import/Export presets as JSON

## Preset Format

```json
{
  "My Preset": {
    "prompt": "a beautiful landscape, 4k, detailed",
    "negative_prompt": "blurry, low quality",
    "steps": 20,
    "sampler": "DPM++ 2M",
    "cfg_scale": 7.0,
    "width": 512,
    "height": 512,
    "styles": []
  }
}
```

## Compatibility

- ForgeUI (tested)
- Automatic1111 WebUI (compatible)

## License

MIT License

## Contributing

Feel free to submit issues and pull requests!