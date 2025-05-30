from collections import defaultdict
from PIL import Image, ImageDraw
import csv

def read_csv(file_path):
    with open(file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = [row for row in csv_reader]
    return data

def calculate_image_size(coordinates, margin):
    # Find the min and max coordinates
    x_values = [float(coord['EASTING']) for coord in coordinates]
    y_values = [float(coord['NORTHING']) for coord in coordinates]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    # Calculate the required image size
    width = max_x - min_x + 100 * margin
    height = max_y - min_y + 100 * margin
    return int(width), int(height)

def draw_environment_dets(coordinates, additional_points, margin):
    # Calculate the dynamic image size
    image_size = calculate_image_size(coordinates, margin)
    # Calculate the scaling factor to fit the rectangle within the image with margin
    corner_coordinates = [coord for coord in coordinates if coord['NAME'].startswith('EDGE')]
    x_values = [float(coord['EASTING']) for coord in corner_coordinates]
    y_values = [float(coord['NORTHING']) for coord in corner_coordinates]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)
    width = max_x - min_x
    height = max_y - min_y
    scaling_factor = min((image_size[0] - 2 * margin) / width, (image_size[1] - 2 * margin) / height)
    # Create a new image
    img = Image.new('RGBA', image_size, color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw the scaled rectangle
    scaled_coordinates = [((float(coord['EASTING']) - min_x) * scaling_factor + margin, (float(coord['NORTHING']) - min_y) * scaling_factor + margin) for coord in corner_coordinates]
    # Draw the scaled rectangle with a thicker boundary
    boundary_thickness = 8  # Adjust thickness as needed
    for i in range(boundary_thickness):
        draw.polygon([
            (coord[0] - i, coord[1] - i) for coord in scaled_coordinates
        ], outline=(0, 0, 0, 255))
        
    return scaling_factor, margin, min_x, min_y, draw, img


def save_image(img):
    # Save the image
    img.save('boundary_map_v3_.png')
    img = img.convert('L')  # Convert to black and white
    img.save('boundary_map_v3.pgm')

def create_yaml(): #hard coded for now
    yaml = open("map_filter_mask.yaml", "w")
    yaml.write("image: boundary_map_v3.pgm\n")
    yaml.write("resolution: 0.050000\n")
    yaml.write("origin: [0.0, 0.0, 0.0]\n")
    yaml.write("negate: 0\noccupied_thresh: 0.65\nfree_thresh: 0.196")
    yaml.close()

if __name__ == "__main__":
    environment_coordinates = read_csv('environment_m.csv')
    additional_points = [point for point in environment_coordinates if point['NAME'] in ('ORIGIN', 'REF01', 'FINISH')]
    margin = 10
    scaling_factor, margin, min_x, min_y, draw, img = draw_environment_dets(environment_coordinates, additional_points, margin)
    save_image(img)
    create_yaml() #hard coded for now

    

