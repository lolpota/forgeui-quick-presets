"""
ForgeUI Quick Presets Extension
A simple extension to save, load, and manage prompt presets.

This extension adds a new tab to the ForgeUI/Automatic1111 web UI that allows users to:
- Save current prompts as presets
- Load saved presets
- Delete presets
- Export/Import presets as JSON
"""

import os
import json
import gradio as gr
from modules import scripts
from modules.shared import opts

PRESETS_FILE = os.path.join(os.path.dirname(__file__), "saved_presets.json")


def load_presets():
    """Load presets from JSON file."""
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_presets(presets):
    """Save presets to JSON file."""
    with open(PRESETS_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, ensure_ascii=False, indent=2)


def get_preset_list():
    """Get list of preset names."""
    presets = load_presets()
    return list(presets.keys())


def save_preset(name, prompt, negative_prompt, styles, steps, sampler, cfg_scale, width, height):
    """Save a new preset."""
    if not name or not name.strip():
        return "Error: Preset name cannot be empty", gr.Dropdown(choices=get_preset_list())
    
    presets = load_presets()
    presets[name.strip()] = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "styles": styles if styles else [],
        "steps": steps,
        "sampler": sampler,
        "cfg_scale": cfg_scale,
        "width": width,
        "height": height
    }
    save_presets(presets)
    return f"✓ Saved preset: {name}", gr.Dropdown(choices=get_preset_list())


def load_preset(name):
    """Load a preset by name."""
    if not name:
        return "", "", [], 20, "DPM++ 2M", 7.0, 512, 512, "No preset selected"
    
    presets = load_presets()
    if name not in presets:
        return "", "", [], 20, "DPM++ 2M", 7.0, 512, 512, f"Error: Preset '{name}' not found"
    
    preset = presets[name]
    return (
        preset.get("prompt", ""),
        preset.get("negative_prompt", ""),
        preset.get("styles", []),
        preset.get("steps", 20),
        preset.get("sampler", "DPM++ 2M"),
        preset.get("cfg_scale", 7.0),
        preset.get("width", 512),
        preset.get("height", 512),
        f"✓ Loaded preset: {name}"
    )


def delete_preset(name):
    """Delete a preset."""
    if not name:
        return "Error: No preset selected", gr.Dropdown(choices=get_preset_list())
    
    presets = load_presets()
    if name in presets:
        del presets[name]
        save_presets(presets)
        return f"✓ Deleted preset: {name}", gr.Dropdown(choices=get_preset_list())
    return f"Error: Preset '{name}' not found", gr.Dropdown(choices=get_preset_list())


def export_presets():
    """Export all presets as JSON string."""
    presets = load_presets()
    return json.dumps(presets, indent=2)


def import_presets(json_str):
    """Import presets from JSON string."""
    try:
        imported = json.loads(json_str)
        if not isinstance(imported, dict):
            return "Error: Invalid format. Expected JSON object.", gr.Dropdown(choices=get_preset_list())
        
        presets = load_presets()
        # Merge imported presets (existing ones with same name are overwritten)
        presets.update(imported)
        save_presets(presets)
        return f"✓ Imported {len(imported)} presets", gr.Dropdown(choices=get_preset_list())
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {e}", gr.Dropdown(choices=get_preset_list())


def get_available_samplers():
    """Get list of available samplers from ForgeUI."""
    try:
        from modules.sd_samplers import samplers
        return [s.name for s in samplers]
    except:
        return [
            "DPM++ 2M", "DPM++ SDE", "DPM++ 2M SDE", "DPM++ 2S a",
            "Euler a", "Euler", "LMS", "Heun", "DDIM", "UniPC"
        ]


def get_available_styles():
    """Get list of available styles from ForgeUI."""
    try:
        from modules.shared import shared_styles
        return [s.name for s in shared_styles]
    except:
        return []


class QuickPresetsExtension(scripts.Script):
    """Gradio script extension for ForgeUI/Automatic1111."""
    
    def __init__(self):
        self.presets_file = PRESETS_FILE
    
    def title(self):
        return "Quick Presets"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible  # Always show in both txt2img and img2img
    
    def ui(self, is_img2img):
        """Create the UI for the extension."""
        with gr.Accordion("Quick Presets", open=False):
            with gr.Row():
                preset_dropdown = gr.Dropdown(
                    choices=get_preset_list(),
                    label="Load Preset",
                    interactive=True
                )
                refresh_btn = gr.Button("🔄", scale=0, min_width=40)
            
            with gr.Row():
                preset_name = gr.Textbox(
                    label="Preset Name",
                    placeholder="Enter name to save as..."
                )
                save_btn = gr.Button("💾 Save Preset", variant="primary")
                delete_btn = gr.Button("🗑️ Delete", variant="secondary")
            
            status_text = gr.Textbox(label="Status", interactive=False)
            
            with gr.Accordion("Import/Export", open=False):
                with gr.Row():
                    export_btn = gr.Button("📤 Export All")
                    export_output = gr.Textbox(label="Exported JSON", lines=5, interactive=False)
                
                with gr.Row():
                    import_input = gr.Textbox(label="Import JSON", lines=5, placeholder="Paste presets JSON here...")
                    import_btn = gr.Button("📥 Import")
            
            # Hidden fields to return values for Apply buttons
            return [
                preset_dropdown, preset_name, save_btn, delete_btn,
                refresh_btn, status_text, export_btn, export_output,
                import_input, import_btn
            ]
        
        # Connect event handlers
        def refresh_list():
            return gr.Dropdown(choices=get_preset_list())
        
        refresh_btn.click(
            fn=refresh_list,
            inputs=[],
            outputs=[preset_dropdown]
        )
        
        save_btn.click(
            fn=save_preset,
            inputs=[preset_name, "prompt", "negative_prompt", "styles",
                    "steps", "sampler_name", "cfg_scale", "width", "height"],
            outputs=[status_text, preset_dropdown]
        )
        
        preset_dropdown.change(
            fn=load_preset,
            inputs=[preset_dropdown],
            outputs=["prompt", "negative_prompt", "styles", "steps",
                    "sampler_name", "cfg_scale", "width", "height", status_text]
        )
        
        delete_btn.click(
            fn=delete_preset,
            inputs=[preset_dropdown],
            outputs=[status_text, preset_dropdown]
        )
        
        export_btn.click(
            fn=export_presets,
            inputs=[],
            outputs=[export_output]
        )
        
        import_btn.click(
            fn=import_presets,
            inputs=[import_input],
            outputs=[status_text, preset_dropdown]
        )
        
        return []


# Additional tab-based interface for preset management
def on_ui_tabs():
    """Create a dedicated tab for preset management."""
    with gr.Blocks() as presets_tab:
        gr.Markdown("# 🎨 Quick Presets Manager")
        gr.Markdown("Save, load, and manage your Stable Diffusion prompt presets.")
        
        with gr.Row():
            with gr.Column(scale=2):
                # Preset List
                preset_list = gr.Dataframe(
                    headers=["Name", "Prompt Preview", "Steps", "Sampler"],
                    datatype=["str", "str", "number", "str"],
                    label="Saved Presets",
                    interactive=False
                )
                
                refresh_list_btn = gr.Button("🔄 Refresh List")
            
            with gr.Column(scale=3):
                # Preset Editor
                gr.Markdown("### Create/Edit Preset")
                
                edit_preset_name = gr.Textbox(label="Preset Name")
                edit_prompt = gr.Textbox(label="Prompt", lines=3)
                edit_negative = gr.Textbox(label="Negative Prompt", lines=2)
                
                with gr.Row():
                    edit_steps = gr.Slider(1, 150, value=20, step=1, label="Steps")
                    edit_sampler = gr.Dropdown(choices=get_available_samplers(), value="DPM++ 2M", label="Sampler")
                
                with gr.Row():
                    edit_width = gr.Slider(256, 2048, value=512, step=64, label="Width")
                    edit_height = gr.Slider(256, 2048, value=512, step=64, label="Height")
                
                edit_cfg = gr.Slider(1, 30, value=7.0, step=0.5, label="CFG Scale")
                
                with gr.Row():
                    save_new_btn = gr.Button("💾 Save as New Preset", variant="primary")
                    update_btn = gr.Button("📝 Update Existing")
                    delete_edit_btn = gr.Button("🗑️ Delete", variant="stop")
                
                status = gr.Textbox(label="Status", interactive=False)
        
        # Import/Export Section
        with gr.Accordion("📦 Import/Export Presets", open=False):
            with gr.Row():
                export_all_btn = gr.Button("📤 Export All Presets to JSON")
                export_json = gr.Textbox(label="Exported JSON", lines=10, interactive=False)
            
            with gr.Row():
                import_json_input = gr.Textbox(label="Import JSON", lines=10, placeholder="Paste presets JSON here...")
                import_btn = gr.Button("📥 Import Presets", variant="primary")
        
        # Event handlers for the tab
        def refresh_preset_list():
            presets = load_presets()
            data = []
            for name, p in presets.items():
                prompt_preview = p.get("prompt", "")[:50] + "..." if len(p.get("prompt", "")) > 50 else p.get("prompt", "")
                data.append([name, prompt_preview, p.get("steps", 20), p.get("sampler", "DPM++ 2M")])
            return data
        
        def load_preset_to_editor(name):
            presets = load_presets()
            if name not in presets:
                return "", "", 20, "DPM++ 2M", 512, 512, 7.0, f"Preset '{name}' not found"
            p = presets[name]
            return (
                p.get("prompt", ""),
                p.get("negative_prompt", ""),
                p.get("steps", 20),
                p.get("sampler", "DPM++ 2M"),
                p.get("width", 512),
                p.get("height", 512),
                p.get("cfg_scale", 7.0),
                f"✓ Loaded '{name}'"
            )
        
        def save_as_new(name, prompt, neg, steps, sampler, w, h, cfg):
            msg, _ = save_preset(name, prompt, neg, [], steps, sampler, cfg, w, h)
            return msg, refresh_preset_list()
        
        refresh_list_btn.click(
            fn=refresh_preset_list,
            inputs=[],
            outputs=[preset_list]
        )
        
        preset_list.select(
            fn=lambda evt: evt.value[0] if evt else "",
            inputs=[],
            outputs=[edit_preset_name]
        )
        
        export_all_btn.click(
            fn=export_presets,
            inputs=[],
            outputs=[export_json]
        )
        
        import_btn.click(
            fn=lambda j: (import_presets(j)[0], refresh_preset_list()),
            inputs=[import_json_input],
            outputs=[status, preset_list]
        )
        
        save_new_btn.click(
            fn=save_as_new,
            inputs=[edit_preset_name, edit_prompt, edit_negative, edit_steps,
                   edit_sampler, edit_width, edit_height, edit_cfg],
            outputs=[status, preset_list]
        )
    
    return [(presets_tab, "Quick Presets", "presets_manager")]


# Register the tab
try:
    from modules import scripts
    scripts.script_callbacks.on_ui_tabs(on_ui_tabs)
except:
    pass


# For direct script loading (alternative method)
if __name__ == "__main__":
    print("Quick Presets Extension for ForgeUI/Automatic1111")
    print("Copy this folder to your extensions directory and restart ForgeUI.")