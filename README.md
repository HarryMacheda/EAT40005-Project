# AMDC L1 Map Conversion for ROS Navigation

This repository contains the scripts and files to convert the AMDC L1 floor plan map into a ROS-compatible `.pgm` and `.yaml` format for Temi robot navigation. The process involves resizing an input image (`amdc_l1_map.png`) and generating metadata based on provided area data.

## Project Overview

- **Input File**: `amdc_l1_map.png` (original floor plan image)
- **Output Files**:
  - `amdc_l1_map.pgm` (grayscale occupancy grid)
  - `amdc_l1_map.yaml` (map metadata for ROS)
- **Script**: `convert_map.py` (Python script for conversion)
- **Directory Structure**:
  ├── maps/
  | ├── amdc_l1_map.png
  │ ├── amdc_l1_map.pgm
  │ ├── amdc_l1_map.yaml
  ├── scripts/
  │ ├── convert_map.py

## Calculations and Assumptions

The following table summarizes the calculations and assumptions made during the map conversion process:

| **Parameter**            | **Value**                             | **Calculation/Method**                                                             | **Assumptions**                                                             |
| ------------------------ | ------------------------------------- | ---------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Real-World Area**      | 2020.31 m²                            | Provided as Internal Gross Area from client data                                   | Map represents the full internal gross area (2020.31 m²) accurately.        |
| **Original Pixel Area**  | Variable (e.g., 800,000 for 1000×800) | `image.shape[0] * image.shape[1]` from the input `amdc_l1_map.png`                 | Original image dimensions are proportional to the real-world area.          |
| **Target Pixels/m²**     | 400                                   | Arbitrarily chosen for sufficient resolution (200-400 is typical for indoor maps)  | 400 pixels/m² provides a balance between detail and performance.            |
| **Pixels/m² (Initial)**  | Variable (e.g., 396)                  | `pixel_area / REAL_WORLD_AREA` based on original image dimensions                  | Image aspect ratio reflects the floor plan's shape (e.g., rectangular).     |
| **Scaling Factor**       | Variable (e.g., 1.007)                | `math.sqrt(target_pixels_per_m2 / pixels_per_m2)` to resize the image              | Scaling preserves the original layout's proportions.                        |
| **Resized Pixel Area**   | Variable (e.g., 639,210 for 894×715)  | `resized_gray.shape[0] * resized_gray.shape[1]` after scaling                      | Resized dimensions align with the target 400 pixels/m².                     |
| **Resolution**           | ~0.05 m/pixel                         | `1.0 / math.sqrt(target_pixels_per_m2)` or adjusted based on resized pixel area    | Resolution is uniform across the map; validated with a known distance.      |
| **Origin (x, y)**        | [-10.0, -10.0]                        | Placeholder; to be updated with real-world coordinates from client or localization | Lower-left corner is offset by -10m in both x and y (pending confirmation). |
| **Occupancy Thresholds** | 0.65 (occupied), 0.196 (free)         | Standard ROS values for interpreting pixel values in `.pgm`                        | Grayscale thresholding (127) separates occupied (0) and free (255) spaces.  |

### Detailed Calculations

1. **Initial Pixels per m²**:

- Example: For an original image of 1000×800 pixels, pixel_area = 800,000.
- Pixels per m² = 800,000 / 2020.31 ≈ 396 pixels/m².

2. **Scaling Factor**:

- Scaling factor = `math.sqrt(400 / 396) ≈ 1.007`.
- Resized dimensions ≈ 1000×1.007 × 800×1.007 ≈ 1007×806 pixels (adjusted in script).

3. **Resized Pixels per m²**:

- For a resized image of 894×715 pixels, resized_area = 639,210.
- Pixels per m² = 639,210 / 2020.31 ≈ 316 pixels/m².

4. **Resolution**:

- Resolution = `1.0 / math.sqrt(400)` ≈ 0.05 m/pixel (target).
- Adjusted resolution = `1.0 / math.sqrt(316)` ≈ 0.0562 m/pixel (based on resized area).
- Final resolution used: ~0.05 m/pixel (to be validated with a known distance).

5. **Origin**:

- Placeholder set to [-10.0, -10.0, 0.0] meters.
- To be updated with actual coordinates from the client (e.g., lower-left corner of AMDC L1).

### Assumptions and Notes

- The original `amdc_l1_map.png` is assumed to be a top-down view with walls and free spaces distinguishable.
- The script applies a binary threshold (127) to convert grayscale to occupancy values (0 = occupied, 255 = free), which may require manual adjustment if the map isn’t pre-processed.
- The resolution and origin are approximate until validated with real-world measurements or client-provided data.
- A question has been sent to the client to provide exact dimensions and a reference coordinate point for precise calibration.

## Usage

1. **Run the Script**:

- Navigate to `scripts/` and execute: `python convert_map.py`.
- Check the console for scaling factor and saved file paths.

2. **Test in ROS**:

- Copy `maps/amdc_l1_map.pgm` and `maps/amdc_l1_map.yaml` to your ROS workspace (e.g., `~/catkin_ws/src/temi_navigation/maps/`).
- Launch the map server: `rosrun map_server map_serve /maps/amdc_l1_map.yaml`.
- Visualize in RViz: `rosrun rviz rviz` and add a `Map` display.

3. **Update Metadata**:

- Adjust `resolution` and `origin` in `amdc_l1_map.yaml` based on client feedback or localization data.

## Contact

For further assistance or to provide map details, contact the project team or client.
