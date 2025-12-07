# Omni Modeler Blender Add-on

This repository contains **Omni Modeler**, a Blender 3D add-on that rapidly scaffolds blockout meshes for vehicles, quadruped creatures, and human mannequins. It is designed to be a starting point for sculpting or detailed modeling, with sensible default modifiers to keep meshes symmetrical and smooth.

## Features
- **One-click blockouts** for cars, quadrupeds, and humans using custom geometry routines.
- Automatic **Mirror** and **Subdivision Surface** modifiers to keep models smooth and symmetrical.
- Configurable **collection placement**, global **scale**, and **auto smooth** shading.
- Accessible from the **3D Viewport Sidebar** under the *Omni Modeler* tab.

## Installation
1. Download `omni_modeler_addon.py` from this repository.
2. In Blender, open **Edit → Preferences → Add-ons → Install...** and select the file.
3. Enable **Omni Modeler**. A new panel will appear in the 3D Viewport sidebar.

## Usage
1. Open the **Omni Modeler** panel (press `N` if the sidebar is hidden).
2. Set the target **Collection**, desired **Scale**, and toggles for **Mirror**, **Subsurf**, and **Auto Smooth**.
3. Click **Create Car Base**, **Create Quadruped**, or **Create Human** to generate a starting mesh at the origin.
4. Continue modeling or sculpting on top of the generated blockout.

## Development
The add-on is contained in a single file for easy distribution. Modify `omni_modeler_addon.py` and reload the add-on in Blender to test changes. No external dependencies are required.
