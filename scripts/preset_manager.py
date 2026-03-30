"""
ForgeUI Quick Presets Extension
A simple extension to save, load, and manage prompt presets.

This extension adds a dedicated tab to ForgeUI/Automatic1111 for managing presets.
"""

import os
import json
import gradio as gr

# Store presets in the extension folder
EXTENSION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRESETS_FILE = os.path.join(EXTENSION_DIR, "saved_presets.json")


def load_presets():
    """Load presets from JSON file."""
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[Quick Presets] Error loading presets: {e}")
            return {}
    return {}


def save_presets_to_file(presets):
    """Save presets to JSON file."""
    try:
        with open(PRESETS_FILE, "w", encoding="utf-8") as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"[Quick Presets] Error saving presets: {e}")
        return False


def get_preset_list():
    """Get list of preset names for dropdown."""
    presets = load_presets()
    return gr.Dropdown(choices=list(presets.keys()))


def get_preset_table_data():
    """Get presets as table data for display."""
    presets = load_presets()
    data = []
    for name, p in presets.items():
        prompt_preview = p.get("prompt", "")[:60] + "..." if len(p.get("prompt", "")) > 60 else p.get("prompt", "")
        data.append([name, prompt_preview, p.get("steps", 20), p.get("sampler", "DPM++ 2M")])
    return data


def get_available_samplers():
    """Get list of available samplers from ForgeUI."""
    try:
        from modules.sd_samplers import samplers
        return [s.name for s in samplers]
    except:
        return [
            "DPM++ 2M", "DPM++ SDE", "DPM++ 2M Karras", "DPM++ 2M SDE Karras",
            "DPM++ 2M SDE Exponential", "DPM++ 2M SDE Heun", "DPM++ 3M SDE",
            "Euler a", "Euler", "LMS", "LMS Karras", "Heun", "DDIM", "UniPC"
        ]


def on_ui_tabs():
    """Create a dedicated tab for preset management."""
    with gr.Blocks() as presets_tab:
        gr.Markdown("# 🎨 Quick Presets Manager")
        gr.Markdown("Save and manage your Stable Diffusion prompt presets. Copy presets to clipboard and paste into txt2img/img2img.")
        
        # Status display
        status_box = gr.Textbox(label="Status", interactive=False, visible=True)
        
        with gr.Row():
            # Left column: Preset List
            with gr.Column(scale=2):
                gr.Markdown("### Saved Presets")
                
                preset_table = gr.Dataframe(
                    headers=["Name", "Prompt Preview", "Steps", "Sampler"],
                    datatype=["str", "str", "number", "str"],
                    label="Your Presets",
                    interactive=False,
                    value=get_preset_table_data()
                )
                
                with gr.Row():
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary")
                    delete_btn = gr.Button("🗑️ Delete Selected", variant="stop")
                
                # Dropdown for selecting preset to load
                preset_select = gr.Dropdown(
                    choices=list(load_presets().keys()),
                    label="Select Preset",
                    interactive=True
                )
                load_btn = gr.Button("📥 Load Preset", variant="primary")
            
            # Right column: Preset Editor
            with gr.Column(scale=3):
                gr.Markdown("### Create/Edit Preset")
                
                preset_name = gr.Textbox(
                    label="Preset Name",
                    placeholder="Enter a name for this preset..."
                )
                
                prompt_box = gr.Textbox(
                    label="Prompt",
                    lines=4,
                    placeholder="Enter your positive prompt here..."
                )
                
                negative_box = gr.Textbox(
                    label="Negative Prompt",
                    lines=2,
                    placeholder="Enter negative prompt here..."
                )
                
                with gr.Row():
                    steps_slider = gr.Slider(
                        minimum=1,
                        maximum=150,
                        value=20,
                        step=1,
                        label="Steps"
                    )
                    sampler_dropdown = gr.Dropdown(
                        choices=get_available_samplers(),
                        value="DPM++ 2M",
                        label="Sampler"
                    )
                
                with gr.Row():
                    width_slider = gr.Slider(
                        minimum=256,
                        maximum=2048,
                        value=512,
                        step=64,
                        label="Width"
                    )
                    height_slider = gr.Slider(
                        minimum=256,
                        maximum=2048,
                        value=512,
                        step=64,
                        label="Height"
                    )
                
                cfg_slider = gr.Slider(
                    minimum=1,
                    maximum=30,
                    value=7.0,
                    step=0.5,
                    label="CFG Scale"
                )
                
                with gr.Row():
                    save_btn = gr.Button("💾 Save Preset", variant="primary")
                    overwrite_btn = gr.Button("✏️ Overwrite Selected", variant="secondary")
        
        # Import/Export Section
        with gr.Accordion("📦 Import/Export", open=False):
            with gr.Row():
                with gr.Column():
                    export_btn = gr.Button("📤 Export All to JSON")
                    export_output = gr.Textbox(
                        label="Exported JSON (copy this)",
                        lines=6,
                        interactive=False
                    )
            with gr.Row():
                with gr.Column():
                    import_input = gr.Textbox(
                        label="Import JSON",
                        lines=6,
                        placeholder="Paste presets JSON here..."
                    )
                    import_btn = gr.Button("📥 Import from JSON", variant="primary")
        
        # Copy Section
        with gr.Accordion("📋 Quick Copy", open=False):
            gr.Markdown("Copy preset values to clipboard for pasting into txt2img/img2img")
            copy_output = gr.Textbox(
                label="Formatted Prompt (copy and paste into txt2img)",
                lines=4,
                interactive=False
            )
            format_btn = gr.Button("📋 Format for Copying")
        
        # ========== Event Handlers ==========
        
        def refresh_all():
            presets = load_presets()
            return (
                gr.Dropdown(choices=list(presets.keys())),
                get_preset_table_data(),
                "✓ List refreshed"
            )
        
        def save_new_preset(name, prompt, negative, steps, sampler, width, height, cfg):
            if not name or not name.strip():
                return gr.Dropdown(), get_preset_table_data(), "❌ Error: Preset name cannot be empty"
            
            name = name.strip()
            presets = load_presets()
            
            if name in presets:
                return gr.Dropdown(), get_preset_table_data(), f"❌ Error: Preset '{name}' already exists. Use Overwrite to replace it."
            
            presets[name] = {
                "prompt": prompt,
                "negative_prompt": negative,
                "steps": int(steps),
                "sampler": sampler,
                "width": int(width),
                "height": int(height),
                "cfg_scale": float(cfg)
            }
            
            if save_presets_to_file(presets):
                return (
                    gr.Dropdown(choices=list(presets.keys())),
                    get_preset_table_data(),
                    f"✓ Saved preset: {name}"
                )
            return gr.Dropdown(), get_preset_table_data(), "❌ Error: Failed to save preset"
        
        def overwrite_preset(name, prompt, negative, steps, sampler, width, height, cfg):
            if not name or not name.strip():
                return gr.Dropdown(), get_preset_table_data(), "❌ Error: Select a preset first or enter a name"
            
            name = name.strip()
            presets = load_presets()
            
            presets[name] = {
                "prompt": prompt,
                "negative_prompt": negative,
                "steps": int(steps),
                "sampler": sampler,
                "width": int(width),
                "height": int(height),
                "cfg_scale": float(cfg)
            }
            
            if save_presets_to_file(presets):
                return (
                    gr.Dropdown(choices=list(presets.keys())),
                    get_preset_table_data(),
                    f"✓ Overwritten preset: {name}"
                )
            return gr.Dropdown(), get_preset_table_data(), "❌ Error: Failed to save preset"
        
        def load_selected_preset(selected_name):
            if not selected_name:
                return "", "", 20, "DPM++ 2M", 512, 512, 7.0, "❌ No preset selected"
            
            presets = load_presets()
            if selected_name not in presets:
                return "", "", 20, "DPM++ 2M", 512, 512, 7.0, f"❌ Error: Preset '{selected_name}' not found"
            
            p = presets[selected_name]
            return (
                p.get("prompt", ""),
                p.get("negative_prompt", ""),
                p.get("steps", 20),
                p.get("sampler", "DPM++ 2M"),
                p.get("width", 512),
                p.get("height", 512),
                p.get("cfg_scale", 7.0),
                f"✓ Loaded preset: {selected_name}"
            )
        
        def delete_selected_preset(selected_name):
            if not selected_name:
                return gr.Dropdown(), get_preset_table_data(), "❌ No preset selected"
            
            presets = load_presets()
            if selected_name in presets:
                del presets[selected_name]
                save_presets_to_file(presets)
                return (
                    gr.Dropdown(choices=list(presets.keys())),
                    get_preset_table_data(),
                    f"✓ Deleted preset: {selected_name}"
                )
            return gr.Dropdown(), get_preset_table_data(), f"❌ Error: Preset '{selected_name}' not found"
        
        def export_all_presets():
            presets = load_presets()
            if not presets:
                return "No presets to export"
            return json.dumps(presets, indent=2)
        
        def import_presets_from_json(json_str):
            if not json_str or not json_str.strip():
                return gr.Dropdown(), get_preset_table_data(), "❌ Error: No JSON provided"
            
            try:
                imported = json.loads(json_str)
                if not isinstance(imported, dict):
                    return gr.Dropdown(), get_preset_table_data(), "❌ Error: Invalid format. Expected JSON object with preset names as keys."
                
                presets = load_presets()
                count = len(imported)
                presets.update(imported)
                save_presets_to_file(presets)
                
                return (
                    gr.Dropdown(choices=list(presets.keys())),
                    get_preset_table_data(),
                    f"✓ Imported {count} presets"
                )
            except json.JSONDecodeError as e:
                return gr.Dropdown(), get_preset_table_data(), f"❌ Error parsing JSON: {e}"
        
        def format_for_copy(name, prompt, negative, steps, sampler, width, height, cfg):
            if not prompt and not name:
                return "Enter a prompt or load a preset first"
            
            formatted = f"""Prompt: {prompt}
Negative: {negative}
Steps: {steps}, Sampler: {sampler}
Size: {width}x{height}, CFG: {cfg}"""
            return formatted
        
        # ========== Wire Up Events ==========
        
        refresh_btn.click(
            fn=refresh_all,
            inputs=[],
            outputs=[preset_select, preset_table, status_box]
        )
        
        save_btn.click(
            fn=save_new_preset,
            inputs=[preset_name, prompt_box, negative_box, steps_slider, 
                    sampler_dropdown, width_slider, height_slider, cfg_slider],
            outputs=[preset_select, preset_table, status_box]
        )
        
        overwrite_btn.click(
            fn=overwrite_preset,
            inputs=[preset_name, prompt_box, negative_box, steps_slider,
                    sampler_dropdown, width_slider, height_slider, cfg_slider],
            outputs=[preset_select, preset_table, status_box]
        )
        
        load_btn.click(
            fn=load_selected_preset,
            inputs=[preset_select],
            outputs=[prompt_box, negative_box, steps_slider, sampler_dropdown,
                    width_slider, height_slider, cfg_slider, status_box]
        )
        
        # Also load when dropdown selection changes
        preset_select.change(
            fn=load_selected_preset,
            inputs=[preset_select],
            outputs=[prompt_box, negative_box, steps_slider, sampler_dropdown,
                    width_slider, height_slider, cfg_slider, status_box]
        )
        
        delete_btn.click(
            fn=delete_selected_preset,
            inputs=[preset_select],
            outputs=[preset_select, preset_table, status_box]
        )
        
        export_btn.click(
            fn=export_all_presets,
            inputs=[],
            outputs=[export_output]
        )
        
        import_btn.click(
            fn=import_presets_from_json,
            inputs=[import_input],
            outputs=[preset_select, preset_table, status_box]
        )
        
        format_btn.click(
            fn=format_for_copy,
            inputs=[preset_name, prompt_box, negative_box, steps_slider,
                    sampler_dropdown, width_slider, height_slider, cfg_slider],
            outputs=[copy_output]
        )
        
        # Sync preset name dropdown with name textbox when loading
        def sync_name_from_dropdown(selected_name):
            return selected_name if selected_name else ""
        
        preset_select.change(
            fn=sync_name_from_dropdown,
            inputs=[preset_select],
            outputs=[preset_name]
        )
    
    return [(presets_tab, "Quick Presets", "extension_quick_presets")]


# Register the tab when module loads
try:
    from modules import script_callbacks
    script_callbacks.on_ui_tabs(on_ui_tabs)
    print("[Quick Presets] Extension loaded successfully!")
except ImportError:
    print("[Quick Presets] Warning: Could not register UI tab. Make sure this is loaded in ForgeUI/Automatic1111")
except Exception as e:
    print(f"[Quick Presets] Error during initialization: {e}")