import streamlit as st
from PIL import Image
import numpy as np
import kociemba

# Map RGB to color code (this is a simplification — improve it for better accuracy)
def closest_color(rgb):
    color_map = {
        'W': (255, 255, 255),
        'Y': (255, 255, 0),
        'R': (255, 0, 0),
        'O': (255, 165, 0),
        'G': (0, 128, 0),
        'B': (0, 0, 255),
    }
    min_dist = float('inf')
    closest = 'W'
    for k, v in color_map.items():
        dist = np.linalg.norm(np.array(rgb) - np.array(v))
        if dist < min_dist:
            min_dist = dist
            closest = k
    return closest

def get_dominant_color(image):
    image = image.resize((300, 300))
    pixels = np.array(image)
    grid = []
    step = 100
    for y in range(0, 300, step):
        for x in range(0, 300, step):
            region = pixels[y+25:y+75, x+25:x+75]
            avg_color = tuple(np.mean(region.reshape(-1, 3), axis=0).astype(int))
            grid.append(closest_color(avg_color))
    return grid

def build_kociemba_string(color_dict):
    face_order = ['U', 'R', 'F', 'D', 'L', 'B']
    face_map = {
        'Up': 'U', 'Right': 'R', 'Front': 'F',
        'Down': 'D', 'Left': 'L', 'Back': 'B'
    }
    cube_string = ''
    for face in face_order:
        for label, code in face_map.items():
            if code == face:
                cube_string += ''.join(color_dict[label])
    return cube_string

def explain_move(move):
    explanations = {
        "R": "Turn the Right face clockwise",
        "R'": "Turn the Right face counterclockwise",
        "R2": "Turn the Right face 180 degrees",
        "L": "Turn the Left face clockwise",
        "L'": "Turn the Left face counterclockwise",
        "L2": "Turn the Left face 180 degrees",
        "U": "Turn the Up face clockwise",
        "U'": "Turn the Up face counterclockwise",
        "U2": "Turn the Up face 180 degrees",
        "D": "Turn the Down face clockwise",
        "D'": "Turn the Down face counterclockwise",
        "D2": "Turn the Down face 180 degrees",
        "F": "Turn the Front face clockwise",
        "F'": "Turn the Front face counterclockwise",
        "F2": "Turn the Front face 180 degrees",
        "B": "Turn the Back face clockwise",
        "B'": "Turn the Back face counterclockwise",
        "B2": "Turn the Back face 180 degrees",
    }
    return explanations.get(move, "Unknown move")

st.title("🧠 Rubik's Cube Solver with AI")
st.write("Upload images of each face of your Rubik's Cube.")

face_labels = ["Front", "Back", "Left", "Right", "Up", "Down"]
face_images = {}
color_dict = {}

for face in face_labels:
    uploaded_file = st.file_uploader(f"Upload {face} face image", type=["jpg", "png", "jpeg"], key=face)
    if uploaded_file:
        image = Image.open(uploaded_file).convert('RGB')
        st.image(image, caption=f"{face} Face", use_column_width=True)
        face_images[face] = image

if st.button("🔍 Detect & Solve"):
    if len(face_images) != 6:
        st.error("Please upload all 6 face images before solving.")
    else:
        for face, img in face_images.items():
            colors = get_dominant_color(img)
            color_dict[face] = colors
            st.text(f"{face} Colors: {colors}")

        cube_str = build_kociemba_string(color_dict)
        st.text(f"Cube String: {cube_str}")

        try:
            solution = kociemba.solve(cube_str)
            st.success("Solution Steps:")
            st.code(solution)

            # Step-by-step explanation
            moves = solution.split()
            st.write("### Step-by-step explanation:")
            for i, move in enumerate(moves, 1):
                st.write(f"{i}. {explain_move(move)}")

        except Exception as e:
            st.error(f"Could not solve cube: {str(e)}")
#python -m streamlit run rubiks_solver_app.py