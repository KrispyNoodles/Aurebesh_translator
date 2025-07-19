# chatgpt cooked code to convert bounding boxes to re-ordered text
def decode_boxes_to_text(boxes, names, y_thresh=15):
    
    # This assumes that the text is written from left to right and top to bottom
    # the purpose of this array is to extract the y & x coordinate of each box and its classes
    points = []

    for b in boxes:

        # extracting the x and y coordiantes of each bounding box
        x1, y1, _, _ = b.xyxy[0].tolist()

        # extracting the class ID of the object as an integer of the classification array
        class_id_int = int(b.cls[0].item())

        # appending the x, y and class of the object
        points.append((y1, x1, names[class_id_int]))

    # Sort the values from y1 (top to bottom) and then x1 (left to right)
    # p is the key variable being used and p[0] and p[1] is what it is being arranged by
    points.sort(key=lambda p: (p[0], p[1]))

    # represents the final sentences
    lines = []

    # temporary list of characters on the current line
    current_line = []

    # a marker to track theu y position of the previous character
    last_y = None

    # looping through the different characters identified from the model
    for y, x, char in points:
        
        # If last_y is None, this is the first character, so start a new line.
        # If the absolute difference between y and the last_y is small (within y_thresh),
        # the characters are considered to be on the same line
        if last_y is None or abs(y - last_y) <= y_thresh:

            # if the y's are similar that the character is appended
            current_line.append((x, char))

        else:

            # the new character is out of the threshold and 
            # assumed to be a new character in the next line
            lines.append(current_line)

            # the new line is then restarted to contain that new character
            current_line = [(x, char)]
        
        # Update last_y to the current character's y-position
        # (i.e. the most recently processed character vertically)
        last_y = y

    if current_line:

        # appending the last line when it has finished processing
        lines.append(current_line)

    # Printing the finalized text
    text = []

    for line in lines:

        line_text = ""
        
        # the previous sort was by (y, x), which groups characters line-by-line (top to bottom),
        # but slight variations in y-coordinates might cause characters in the same visual line to be misaligned or out of order horizontally.
        # So we sort again by x to ensure correct left-to-right character order within each line.

        # the line array contains only the x-axis and the character
        line.sort(key=lambda p: p[0])

        # printing out the line
        for _,char in line:
            line_text += char

        # adding the line_text into the array of texts
        text.append(line_text)

    # joining the item in the list with a space between them
    return " ".join(text)  

# inferncing with the model_trained
from pathlib import Path
from ultralytics import YOLO
from config import llm
from prompts import user_message, system_prompt
from langchain_core.messages import HumanMessage, SystemMessage


# declaring the model path
model = YOLO("./model/best.pt")

# refers to the list of calssifcaiton it has
classes = model.names

# infers an image
def arubesh_inference(image:Path):

    # running a prediction
    # Run prediction on an image
    # conf is filtering the confidence below 0.3 to be out
    # image size to be the same as what it was trained on previously
    results = model.predict(source=image, save=False, conf=0.30, imgsz=416)

    result = results[0]

    # saving the results
    result.save(filename="result.jpg")
    print("results saved")

    sentence = decode_boxes_to_text(result.boxes, classes)

    print(f"Sentence predicted using YOLO model is: {sentence}")

    # spelling corrector
    if len(sentence) == 0:
        return("No arubesh detected unfortunately, are you a Star Trek fan?")

    else:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_message(sentence))])
        corrected_text = response.content

    return corrected_text