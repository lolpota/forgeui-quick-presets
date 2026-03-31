"""
ForgeUI Quick Presets Extension - Mobile Friendly Version
A simple extension to save, load, and manage prompt presets.
Designed for mobile-friendly use with essential settings only.
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


def get_preset_choices():
    """Get list of preset names for dropdown."""
    presets = load_presets()
    return list(presets.keys())


def get_available_samplers():
    """Get list of available samplers from ForgeUI."""
    try:
        from modules.sd_samplers import samplers
        return [s.name for s in samplers]
    except:
        return ["DPM++ 2M", "Euler a", "Euler", "DDIM", "UniPC"]


def on_ui_tabs():
    """Create a mobile-friendly preset management tab."""
    
    # Custom CSS for mobile-friendly layout
    custom_css = """
    .preset-mobile-container {
        max-width: 100%;
        padding: 10px;
    }
    .preset-mobile-container .gr-button {
        min-height: 44px !important;
        font-size: 16px !important;
    }
    .preset-mobile-container .gr-text-input, 
    .preset-mobile-container .gr-textbox textarea {
        font-size: 16px !important;
    }
    .preset-status-ok {
        background-color: #2d5a27 !important;
        color: white !important;
    }
    .preset-status-error {
        background-color: #5a2727 !important;
        color: white !important;
    }
    """
    
    with gr.Blocks(css=custom_css) as presets_tab:
        
        # ========== PRESET SELECTOR ==========
        gr.Markdown("## 📱 Presets")
        
        with gr.Row():
            preset_dropdown = gr.Dropdown(
                choices=get_preset_choices(),
                label="📂 Your Presets",
                interactive=True,
                scale=4
            )
        
        with gr.Row():
            load_btn = gr.Button("📥 Load", variant="primary", size="lg")
            delete_btn = gr.Button("🗑️ Delete", variant="secondary", size="lg")
        
        # Status display
        status_box = gr.Textbox(label="", interactive=False, lines=1, placeholder="Ready")
        
        # ========== QUICK PROMPT (Main Focus) ==========
        gr.Markdown("---")
        
        preset_name = gr.Textbox(
            label="✏️ Preset Name",
            placeholder="Enter name...",
            lines=1
        )
        
        prompt_box = gr.Textbox(
            label="✨ Prompt",
            placeholder="Your positive prompt...",
            lines=3,
            max_lines=6
        )
        
        negative_box = gr.Textbox(
            label="🚫 Negative Prompt",
            placeholder="Things to avoid...",
            lines=2,
            max_lines=4
        )
        
        # ========== BASIC SETTINGS (Collapsed by default) ==========
        with gr.Accordion("⚙️ Settings", open=False):
            with gr.Row():
                steps_slider = gr.Slider(1, 150, value=20, step=1, label="Steps")
                cfg_slider = gr.Slider(1, 30, value=7, step=0.5, label="CFG Scale")
            
            with gr.Row():
                width_slider = gr.Slider(256, 2048, value=512, step=64, label="Width")
                height_slider = gr.Slider(256, 2048, value=512, step=64, label="Height")
            
            sampler_dropdown = gr.Dropdown(
                choices=get_available_samplers(),
                value="DPM++ 2M",
                label="Sampler"
            )
        
        # ========== ACTION BUTTONS ==========
        with gr.Row():
            save_btn = gr.Button("💾 Save New", variant="primary", size="lg")
            overwrite_btn = gr.Button("✏️ Overwrite", variant="secondary", size="lg")
        
        # ========== IMPORT/EXPORT (Collapsed) ==========
        with gr.Accordion("📦 Import/Export", open=False):
            with gr.Row():
                export_btn = gr.Button("📤 Export All", size="sm")
                import_btn = gr.Button("📥 Import", size="sm")
            
            export_output = gr.Textbox(
                label="Exported JSON",
                lines=4,
                interactive=False,
                placeholder="Click Export to generate..."
            )
            
            import_input = gr.Textbox(
                label="Paste JSON to Import",
                lines=4,
                placeholder="Paste presets JSON here..."
            )
        
        # ========== COPY OUTPUT ==========
        with gr.Accordion("📋 Copy Prompt", open=False):
            copy_output = gr.Textbox(
                label="Copy this to txt2img:",
                lines=4,
                interactive=False
            )
            copy_btn = gr.Button("📋 Format for Copy", size="sm")
        
        # ========== EVENT HANDLERS ==========
        
        def update_status(msg, is_error=False):
            return msg
        
        def do_save_new(name, prompt, negative, steps, sampler, width, height, cfg):
            if not name or not name.strip():
                return gr.Dropdown(choices=get_preset_choices()), "❌ Enter a name first"
            
            name = name.strip()
            presets = load_presets()
            
            if name in presets:
                return gr.Dropdown(choices=get_preset_choices()), f"❌ '{name}' exists - use Overwrite"
            
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
                return gr.Dropdown(choices=get_preset_choices()), f"✅ Saved: {name}"
            return gr.Dropdown(choices=get_preset_choices()), "❌ Save failed"
        
        def do_overwrite(name, prompt, negative, steps, sampler, width, height, cfg):
            if not name or not name.strip():
                return gr.Dropdown(choices=get_preset_choices()), "❌ Enter a name first"
            
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
                return gr.Dropdown(choices=get_preset_choices()), f"✅ Updated: {name}"
            return gr.Dropdown(choices=get_preset_choices()), "❌ Save failed"
        
        def do_load(selected_name):
            if not selected_name:
                return "", "", 20, "DPM++ 2M", 512, 512, 7.0, "", "❌ Select a preset"
            
            presets = load_presets()
            if selected_name not in presets:
                return "", "", 20, "DPM++ 2M", 512, 512, 7.0, "", f"❌ Not found: {selected_name}"
            
            p = presets[selected_name]
            return (
                p.get("prompt", ""),
                p.get("negative_prompt", ""),
                p.get("steps", 20),
                p.get("sampler", "DPM++ 2M"),
                p.get("width", 512),
                p.get("height", 512),
                p.get("cfg_scale", 7.0),
                selected_name,
                f"✅ Loaded: {selected_name}"
            )
        
        def do_delete(selected_name):
            if not selected_name:
                return gr.Dropdown(choices=get_preset_choices()), "❌ Select a preset first"
            
            presets = load_presets()
            if selected_name in presets:
                del presets[selected_name]
                save_presets_to_file(presets)
                return gr.Dropdown(choices=get_preset_choices()), f"✅ Deleted: {selected_name}"
            return gr.Dropdown(choices=get_preset_choices()), f"❌ Not found: {selected_name}"
        
        def do_export():
            presets = load_presets()
            if not presets:
                return "No presets saved"
            return json.dumps(presets, indent=2)
        
        def do_import(json_str):
            if not json_str or not json_str.strip():
                return gr.Dropdown(choices=get_preset_choices()), "❌ No JSON provided"
            
            try:
                imported = json.loads(json_str)
                if not isinstance(imported, dict):
                    return gr.Dropdown(choices=get_preset_choices()), "❌ Invalid format"
                
                # Validate preset structure
                required_fields = ['prompt', 'negative', 'steps', 'sampler', 'width', 'height', 'cfg']
                invalid = []
                for name, preset in imported.items():
                    if not isinstance(preset, dict):
                        invalid.append(name)
                        continue
                    missing = [f for f in required_fields if f not in preset]
                    if missing:
                        invalid.append(f"{name} (missing: {', '.join(missing)})")
                
                if invalid:
                    return gr.Dropdown(choices=get_preset_choices()), f"⚠️ Some presets invalid: {', '.join(invalid[:3])}"
                
                presets = load_presets()
                count = len(imported)
                presets.update(imported)
                save_presets_to_file(presets)
                return gr.Dropdown(choices=get_preset_choices()), f"✅ Imported {count} presets"
            except json.JSONDecodeError as e:
                return gr.Dropdown(choices=get_preset_choices()), f"❌ JSON error: {e}"
        
        def do_format_copy(name, prompt, negative, steps, sampler, width, height, cfg):
            if not prompt and not name:
                return "Load or enter a preset first"
            
            return f"""Steps: {steps}, Sampler: {sampler}, CFG: {cfg}
Size: {width}x{height}

Prompt:
{prompt}

Negative:
{negative}"""
        
        # ========== WIRE UP EVENTS ==========
        
        load_btn.click(
            fn=do_load,
            inputs=[preset_dropdown],
            outputs=[prompt_box, negative_box, steps_slider, sampler_dropdown,
                    width_slider, height_slider, cfg_slider, preset_name, status_box]
        )
        
        preset_dropdown.change(
            fn=do_load,
            inputs=[preset_dropdown],
            outputs=[prompt_box, negative_box, steps_slider, sampler_dropdown,
                    width_slider, height_slider, cfg_slider, preset_name, status_box]
        )
        
        delete_btn.click(
            fn=do_delete,
            inputs=[preset_dropdown],
            outputs=[preset_dropdown, status_box]
        )
        
        save_btn.click(
            fn=do_save_new,
            inputs=[preset_name, prompt_box, negative_box, steps_slider,
                    sampler_dropdown, width_slider, height_slider, cfg_slider],
            outputs=[preset_dropdown, status_box]
        )
        
        overwrite_btn.click(
            fn=do_overwrite,
            inputs=[preset_name, prompt_box, negative_box, steps_slider,
                    sampler_dropdown, width_slider, height_slider, cfg_slider],
            outputs=[preset_dropdown, status_box]
        )
        
        export_btn.click(
            fn=do_export,
            outputs=[export_output]
        )
        
        import_btn.click(
            fn=do_import,
            inputs=[import_input],
            outputs=[preset_dropdown, status_box]
        )
        
        copy_btn.click(
            fn=do_format_copy,
            inputs=[preset_name, prompt_box, negative_box, steps_slider,
                    sampler_dropdown, width_slider, height_slider, cfg_slider],
            outputs=[copy_output]
        )
    
    return [(presets_tab, "📱 Presets", "extension_quick_presets")]


# Register the tab
try:
    from modules import script_callbacks
    script_callbacks.on_ui_tabs(on_ui_tabs)
    print("[Quick Presets] Mobile-friendly version loaded!")
except ImportError:
    print("[Quick Presets] Warning: Could not register UI tab")
except Exception as e:
    print(f"[Quick Presets] Error during initialization: {e}")