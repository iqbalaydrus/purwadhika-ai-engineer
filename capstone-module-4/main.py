import streamlit as st

DISCORD_CHANNEL_NAME = st.secrets["DISCORD_CHANNEL_NAME"]


def classify_image(image):
    from ultralytics import YOLO
    from PIL import Image
    import supervision as sv
    from collections import Counter

    model = YOLO("capstone-module-4/training/best.pt")
    image = Image.open(image)
    result = model.predict(image, verbose=False)[0]
    detection = sv.Detections.from_ultralytics(result).with_nms()
    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    annotated_image = image.copy()
    annotated_image = box_annotator.annotate(
        scene=annotated_image,
        detections=detection,
    )
    annotated_image = label_annotator.annotate(
        scene=annotated_image,
        detections=detection,
    )
    v_count = Counter(detection.data["class_name"])
    v_count_str = ""
    for key, value in v_count.items():
        v_count_str += f"{key}={value}\n"
    st.write(f"Vehicle count:\n{v_count_str}")
    st.image(annotated_image)


st.title("Vehicle Counter")
st.write(
    """Upload an image with one or multiple car, bus, or van in it. And we'll output the count of each vechicle type."""
)

for k, v in st.session_state.items():
    st.session_state[k] = v

if not st.session_state.get("token") or st.session_state.token != DISCORD_CHANNEL_NAME:
    st.text_input("Enter our discord channel name - needed for auth:", key="token")
    st.write(":red[Incorrect channel name]")
else:
    if uploaded_file := st.file_uploader("Upload image"):
        classify_image(uploaded_file)
