from dataclasses import dataclass, field
from typing import List, Any
import gradio as gr
from gradio_imagemeta import ImageMeta
from gradio_imagemeta.helpers import extract_metadata, add_metadata, transfer_metadata
from gradio_propertysheet import PropertySheet
from gradio_propertysheet.helpers import  flatten_dataclass_with_labels
from pathlib import Path

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)


@dataclass
class ImageSettings:
    """Configuration for image metadata settings."""
    model: str = field(default="", metadata={"label": "Model"})
    f_number: str = field(default="", metadata={"label": "FNumber"})
    iso_speed_ratings: str = field(default="", metadata={"label": "ISOSpeedRatings"})
    s_churn: float = field(
        default=0.0,
        metadata={"component": "slider", "label": "Schurn", "minimum": 0.0, "maximum": 1.0, "step": 0.01},
    )

@dataclass
class PropertyConfig:
    """Root configuration for image properties, including nested image settings."""
    image_settings: ImageSettings = field(default_factory=ImageSettings,  metadata={"label": "Image Settings"})
    description: str = field(default="", metadata={"label": "Description"})

def handle_load_metadata(image_data: ImageMeta | None) -> List[Any]:
    """
    Processes image metadata by calling the agnostic `transfer_metadata` helper.
    """
    if not image_data or not hasattr(image_data, 'path'):
        return [gr.skip()] * len(output_fields)

    metadata = extract_metadata(image_data, only_custom_metadata=True)
    if not metadata:
        return [gr.skip()] * len(output_fields)
        
    # --- UI-Specific Configuration ---
    # Define the map that tells the helper how to process the PropertySheet.
    sheet_map = {
        id(property_sheet): {
            "type": PropertyConfig, 
            "prefixes": [] # No prefixes needed for this simple case
        }
    }
    
    # Call the agnostic helper function to do the heavy lifting.
    return transfer_metadata(
        output_fields=output_fields,
        metadata=metadata,
        propertysheet_map=sheet_map,
        remove_prefix_from_keys=True
    )

def save_image_with_metadata(
    image_data: Any, 
    sheet_state: PropertyConfig,
    model: str, 
    f_number: str, 
    iso: str, 
    s_churn_val: float, 
    description: str
) -> str | None:
    """
    Saves an image with updated metadata, merging data from the PropertySheet
    and individual UI components.
    This example deals with the PropertySheet component and the individual gradio components. 
    Since they have the same labels here, we'll simply replace the metadata with each other's values.
    """
    if not image_data:
        return None
   
   
    metadata = flatten_dataclass_with_labels(sheet_state)
    individual_component_values = {
        "Model": model,
        "FNumber": f_number,
        "ISOSpeedRatings": iso,
        "Schurn": s_churn_val,
        "Description": description
    }
   
    metadata["Image Settings - Model"] = individual_component_values["Model"]
    metadata["Image Settings - FNumber"] = individual_component_values["FNumber"]
    metadata["Image Settings - ISOSpeedRatings"] = individual_component_values["ISOSpeedRatings"]
    metadata["Image Settings - Schurn"] = individual_component_values["Schurn"]
    metadata["Description"] = individual_component_values["Description"]
   
    final_metadata = {str(key): value for key, value in metadata.items()}
    
    new_filepath = output_dir / "image_with_meta.png"
    add_metadata(image_data, new_filepath, final_metadata)
    
    return str(new_filepath)

initial_property_from_meta_config = PropertyConfig()

with gr.Blocks() as demo:
    gr.Markdown("# ImageMeta Component Demo")
    gr.Markdown(
        """
        **To Test:**
        1. Upload an image with EXIF or PNG metadata using either the "Upload Imagem (Custom metadata only)" component or the "Upload Imagem (all metadata)" component.
        2. Click the 'Info' icon (ⓘ) in the top-left of the image component to view the metadata panel.
        3. Click 'Load Metadata' in the popup to populate the fields below with metadata values (`Model`, `FNumber`, `ISOSpeedRatings`, `Schurn`, `Description`).
        4. The section below displays how metadata is rendered in components and the `PropertySheet` custom component, showing the hierarchical structure of the image settings.
        5. In the "Metadata Viewer" section, you can add field values as metadata to a previously uploaded image in "Upload Image (Custom metadata only)." Then click 'Add metadata and save image' to save a new image with the metadata.
        """
    )
    property_sheet_state = gr.State(value=initial_property_from_meta_config)
    with gr.Row():
        img_custom = ImageMeta(
            label="Upload Image (Custom metadata only)",
            type="filepath",
            width=600,
            height=400,            
            popup_metadata_height=350,
            popup_metadata_width=550,
            interactive=True,
            only_custom_metadata=True,
            #value=""
                       
        )
        img_all = ImageMeta(
            label="Upload Image (All metadata)",
            only_custom_metadata=False,
            type="filepath",
            width=600,
            height=400,            
            popup_metadata_height=350,
            popup_metadata_width=550,
            interactive=True
        )

    gr.Markdown("## Metadata Viewer")
    gr.Markdown("### Individual Components")
    with gr.Row():
        model_box = gr.Textbox(label="Model")
        fnumber_box = gr.Textbox(label="FNumber")
        iso_box = gr.Textbox(label="ISOSpeedRatings")
        s_churn = gr.Slider(label="Schurn", value=1.0, minimum=0.0, maximum=1.0, step=0.1)
        description_box = gr.Textbox(label="Description", lines=2)
    
    gr.Markdown("### PropertySheet Component")
    with gr.Row():
        property_sheet = PropertySheet(
            value=initial_property_from_meta_config,
            label="Image Settings",
            width=400,
            height=550,
            visible=True,
            root_label="General"
        )    
    gr.Markdown("## Metadata Editor")
    with gr.Row():
        save_button = gr.Button("Add Metadata and Save Image")
        saved_file_output = gr.File(label="Download Image")
   
        
    input_fields = {
        "Model": model_box,
        "FNumber": fnumber_box,
        "ISOSpeedRatings": iso_box,
        "Schurn": s_churn,
        "Description": description_box
    }
    
    output_fields = [
        property_sheet,
        model_box,
        fnumber_box,
        iso_box,
        s_churn,
        description_box
    ]
    
    img_custom.load_metadata(handle_load_metadata, inputs=img_custom, outputs=output_fields)
    img_all.load_metadata(handle_load_metadata, inputs=img_all, outputs=output_fields)
    
    def handle_render_change(updated_config: PropertyConfig, current_state: PropertyConfig):
        """
        Updates the PropertySheet state when its configuration changes.

        Args:
            updated_config: The new PropertyConfig instance from the PropertySheet.
            current_state: The current PropertyConfig state.

        Returns:
            A tuple of (updated_config, updated_config) or (current_state, current_state) if updated_config is None.
        """
        if updated_config is None:
            return current_state, current_state
        return updated_config, updated_config
    
    property_sheet.change(
        fn=handle_render_change,
        inputs=[property_sheet, property_sheet_state],
        outputs=[property_sheet, property_sheet_state]
    )
    save_button.click(
        save_image_with_metadata,
        inputs=[img_custom, property_sheet, *input_fields.values()],
        outputs=[saved_file_output]
    )
   
if __name__ == "__main__":
    demo.launch()