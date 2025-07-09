# ComfyUI Headless Workflow Runner
A script that uses the internals of [ComfyUI](https://github.com/comfyanonymous/ComfyUI) to run a workflow without running a ComfyUI server/GUI or using the API

## Features
- Executes ComfyUI workflow JSON files headlessly
- Auto-detects output nodes (e.g. SaveImage)
- Randomizes seed for KSampler nodes
- Compatible with API-exported workflows

## Usage
1. Clone this repository or copy this script into your ComfyUI directory.
2. Run the script: `python -m scripts.run_workflow`. Don't forget to use the same virtual environment as you would with ComfyUI.
3. Check output images in the `output/` directory

## Requirements
- ComfyUI installed (and script run from within ComfyUI’s package context)
- All required models and other assets in the correct folders
