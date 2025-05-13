import numpy as np
import cv2
import math
import os

# Real-world area in square meters
REAL_WORLD_AREA = 2020.31

# Input and output paths
input_file = '/Users/aarush/Desktop/Year 4 - Sem 1/EAT 40005/FYP/maps/amdc_l1_map.png'
output_dir = '/Users/aarush/Desktop/Year 4 - Sem 1/EAT 40005/FYP/maps'
script_dir = '/Users/aarush/Desktop/Year 4 - Sem 1/EAT 40005/FYP/scripts'
map_name = 'amdc_l1_map'

# Ensure directories exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(script_dir, exist_ok=True)
os.chdir(script_dir)

# Load image
image = cv2.imread(os.path.join(input_file))
if image is None:
    print(f"Error: Image '{input_file}' not found!")
    exit()

# Calculate pixel area and scaling
pixel_area = image.shape[0] * image.shape[1]
target_pixels_per_m2 = 400
pixels_per_m2 = pixel_area / REAL_WORLD_AREA
scaling_factor = math.sqrt(target_pixels_per_m2 / pixels_per_m2)
print(f"Scaling factor: {scaling_factor:.4f}")

# Resize and convert to grayscale
resized = cv2.resize(image, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_CUBIC)
resized_gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

# Save PGM
pgm_path = os.path.join(output_dir, map_name + '.pgm')
cv2.imwrite(pgm_path, resized_gray)

# Calculate resolution (based on resized image)
resized_area = resized_gray.shape[0] * resized_gray.shape[1]
pixels_per_m2 = resized_area / REAL_WORLD_AREA
resolution = 1.0 / math.sqrt(pixels_per_m2)
print(f"Calculated resolution: {resolution:.6f} m/pixel")

# Origin (adjust based on map alignment)
origin_x, origin_y = -10.0, -10.0  # Replace with actual coordinates from floor plan or localization
print(f"Origin set to [{origin_x}, {origin_y}, 0.0] - Update with real-world coordinates!")

# Save YAML
yaml_path = os.path.join(output_dir, map_name + '.yaml')
with open(yaml_path, 'w') as yaml:
    yaml.write(f"image: {map_name}.pgm\n")
    yaml.write(f"resolution: {resolution:.6f}\n")
    yaml.write(f"origin: [{origin_x}, {origin_y}, 0.0]\n")
    yaml.write("negate: 0\n")
    yaml.write("occupied_thresh: 0.65\n")
    yaml.write("free_thresh: 0.196\n")
    
print(f"\n✅ Saved:\n{pgm_path}\n{yaml_path}")
cv2.imshow("Resized Map", resized_gray)
cv2.waitKey(0)
cv2.destroyAllWindows()