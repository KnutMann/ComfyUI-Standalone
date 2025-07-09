import os
import sys
import asyncio
import uuid
import json
import logging
import random

# Copyright (c) 2025 KnutMann
# MIT License

# How to use
# - Export workflow using 'API Export'
# - Put script in ComfyUI subdir 'scripts'
# - Start it from ComfyUI-dir via: python -m scripts.run_workflow (so that Python treats ComfyUI as the root package)
#
# Lessons from troubleshooting:
# - Monkeypatching sys.modules is needed for ComfyUI's absolute-imports when run as a module/script.
# - Workflow JSON exported via the ComfyUI API/GUI does NOT include an "outputs" field, but the internal API requires you to pass the output node IDs manually.
# - Output files (e.g. images) are only written if your workflow contains an explicit output node like SaveImage.
# - If no output files appear, it is likely a problem with the output node.

# Enable debug logging for deeper diagnosis (shows VRAM, device, file scanning, etc.)
#logging.basicConfig(level=logging.DEBUG)

workflow_file = "standalone_workflows/test.json"

# Fix package imports for ComfyUI
COMFY_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, COMFY_PATH)

# Monkeypatch: needed for ComfyUI's absolute imports to work outside "main.py"
sys.modules['utils'] = __import__('utils')
sys.modules['app'] = __import__('app')

from execution import PromptExecutor
from server import PromptServer

# Load workflow. Does not contain 'outputs' field at this point
print(f"Loading Workflow: {workflow_file}")
with open(workflow_file, "r") as f:
    prompt = json.load(f)

# Find all nodes of type KSampler and assign a random seed (64-bit unsigned int)
random_seed = random.randint(0, 2**64 - 1)
for node in prompt.values():
    if isinstance(node, dict) and node.get("class_type") == "KSampler":
        if "inputs" in node and "seed" in node["inputs"]:
            old_seed = node["inputs"]["seed"]
            node["inputs"]["seed"] = random_seed
            print(f"Using random seed: {random_seed}")

# Dynapic output node Detection
# This block finds all SaveImage nodes (adjust list for other output node types).
output_node_types = ["SaveImage"]  # Add e.g. "SaveVideo", "SaveMask" if needed!
outputs = [
    node_id for node_id, node in prompt.items()
    if isinstance(node, dict) and node.get("class_type") in output_node_types
]

if not outputs:
    print("Warnung: Kein Output-Node vom Typ SaveImage gefunden! Workflow wird trotzdem ausgeführt, wird dann wohl ins Leere laufen.")

# Remove any accidental 'outputs' key from prompt dict, just to be safe.
node_dict = {k: v for k, v in prompt.items() if k != "outputs"}

# Setup Asyncio event loop (needed by ComfyUI core!)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

server = PromptServer(loop)
executor = PromptExecutor(server)

# Generate a unique prompt-ID
prompt_id = str(uuid.uuid4())

# Run the workflow
# Must pass: node_dict, prompt_id, empty extra_data, and the outputs list
result = executor.execute(node_dict, prompt_id, {}, outputs)
