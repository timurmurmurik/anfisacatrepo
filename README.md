# PrimeForm Lab (Blender Add-on)

PrimeForm Lab is a concept-first toolkit that accelerates blockouts, relaxes dense meshes without crushing silhouettes, and aligns UV flow for brush-friendly gradients.

## Features
- **Generative Block Scatter:** spawn a cluster of view-oriented block shapes with golden-ratio-biased proportions to explore silhouettes in seconds.
- **Silhouette-Safe Relax:** iterative Laplacian relax that pins borders by default and blends toward the original volume to avoid shrinkage; pins UVs to stabilize texture paint.
- **Flow Align UVs:** rotates each UV island to its dominant axis and normalizes scale for cleaner directional painting and decals.

## Usage
1. Install the GitHub ZIP directly (`Edit > Preferences > Add-ons > Install`) or point Blender to the `primeform_lab` folder. The add-on exposes its entrypoint at the ZIP root so no manual repackaging is required.
2. Open the **PrimeForm** tab in the 3D Viewport sidebar.
3. Run **Generative Block Scatter** to create a design scaffold, then sculpt or boolean against it.
4. Enter **Edit Mode** and use **Silhouette-Safe Relax** on dense selections.
5. With UVs visible in Edit Mode, use **Flow Align UVs** to tidy UV direction before texturing.

## Notes
- Designed for Blender 3.0+ and relies only on built-in modules.
- Operators are undo-aware and scoped to active selection wherever possible.

## Installation troubleshooting
- If you previously tried to install a broken ZIP, remove any `primeform_lab` or `anfisacatrepo*` folders from your Blender add-ons directory before reinstalling.
- After clicking **Install**, make sure to search for "PrimeForm Lab" in the Add-ons list and enable its checkbox. If the checkbox refuses to enable, check the **Help > Toggle System Console** window for Python errors.
- The add-on defensively clears registration state on each enable, so re-enabling after a failed attempt should not complain about already-registered classes.
