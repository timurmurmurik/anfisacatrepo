# Blender Quick Beveled Cube Addon

This repository contains a simple Blender addon that adds a **Quick Beveled Cube** panel to the 3D Viewport sidebar. The panel lets you create cubes with custom dimensions, beveled edges, and optional smooth shading in a single click.

## Installation
1. In Blender, open **Edit → Preferences → Add-ons**.
2. Click **Install…** and select the `blender_quick_addon` folder as a zip archive.
3. Enable **Quick Beveled Cube** from the addon list.

## Usage
1. Switch to **Object Mode** and open the **Sidebar (N)** in the 3D Viewport.
2. In the **Create** tab, find the **Quick Beveled Cube** panel.
3. Adjust width, depth, height, bevel amount, segment count, and smooth shading.
4. Press **Add Quick Beveled Cube** to add the customized mesh to the scene.

## Development Notes
- The addon is defined in `blender_quick_addon/__init__.py` and can be reloaded using Blender's **Text Editor → Run Script** or **F8** reload.
- The code targets Blender 3.0+ and uses `bmesh` for mesh creation and beveling.
