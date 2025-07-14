from collections import Counter
import time
import pyautogui
import easyocr
from PIL import Image, ImageFilter
import numpy as np

def load_word_list(filename="anagrams_words.txt"):
    with open(filename, 'r') as word_list:
        return [line.strip().upper() for line in word_list if line.strip()]

def ocr(screenshot, reader):
    # Binarize the image
    img_array = np.array(screenshot.convert('L'))
    threshold = 30
    img_array = np.where(img_array < threshold, 0, 255).astype(np.uint8)
    binarized_letters = Image.fromarray(img_array)

    detections = reader.readtext(np.array(binarized_letters), allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ', detail=0)

    text_parts = []
    for detection in detections:
        text_parts.append(str(detection).strip())
    text = ''.join(text_parts).upper().replace(' ', '')
    return text

def can_make_word_from_letters(word, letters):
    word_counter = Counter(word)
    letters_counter = Counter(letters)

    for letter, count in word_counter.items():
        if letters_counter[letter] < count:
            return False
    return True

def find_possible_words(letters, word_list):
    letters = letters.upper().replace(" ", "")

    possible_words = []
    for word in word_list:
        if can_make_word_from_letters(word, letters):
            possible_words.append(word)

    # Sort by length (longest first), then alphabetically
    possible_words.sort(key=lambda x: (-len(x), x))
    return possible_words

# Convert each word to numbers, 0 being clicking the left-most letter, 6 being clicking the right-most letter
def convert_word_list_to_click_order(word_list, letters):
    click_order = []
    for i in range(len(word_list)):
        word = word_list[i]
        click_order.append("")
        for letter in word:
            for j in range(len(letters)):
                if letters[j] == letter and str(j) not in click_order[i]:
                    click_order[i] += str(j)
                    break
    return click_order

def calculate_max_points(word_list):
    max_score = 0
    for word in word_list:
        if len(word) == 7:
            max_score += 3000
        elif len(word) == 6:
            max_score += 2000
        elif len(word) == 5:
            max_score += 1200
        elif len(word) == 4:
            max_score += 400
        elif len(word) == 3:
            max_score += 100
    return max_score

def display_results(words, letters):
    print(f"\nWords that can be made from '{letters}':")
    print("=" * 50)

    # Group words by length
    words_by_length = {}
    for word in words:
        length = len(word)
        if length not in words_by_length:
            words_by_length[length] = []
        words_by_length[length].append(word)

    # Display grouped by length
    for length in sorted(words_by_length.keys(), reverse=True):
        print(f"\n{length}-letter words ({len(words_by_length[length])} found, {calculate_max_points(words_by_length[length])} points):")
        words_in_length = words_by_length[length]
        # Display in columns for better readability
        for i in range(0, len(words_in_length), 5):
            row = words_in_length[i:i+5]
            print("  " + "  ".join(f"{word:<12}" for word in row))

    print(f"\nTotal words found: {len(words)}")
    print(f"Total points: {calculate_max_points(words)}")

def execute_clicks(click_order, individual_letter_boxes_coordinates, enter_button_center_coords):
    for word_click_order in click_order:
        for click in word_click_order:
            pyautogui.click(individual_letter_boxes_coordinates[int(click)])
        pyautogui.click(enter_button_center_coords)
        time.sleep(0.075)

def main():
    reader = easyocr.Reader(['en'])

    word_list = load_word_list()
    try:
        start_button_coords = pyautogui.locateOnScreen('./images/start_button.png', confidence=0.7)
        if start_button_coords:
            # Divide by 2 for MacOS Retina display scaling
            start_button_center_coords = ((start_button_coords[0] + start_button_coords[2] / 2) / 2, (start_button_coords[1] + start_button_coords[3] / 2) / 2)
    except pyautogui.ImageNotFoundException:
        print("No start button detected! Please open the game to the start screen and try again.")
        return

    pyautogui.click(start_button_center_coords, clicks=2, interval=0.2)
    time.sleep(1)

    try:
        enter_button_coords = pyautogui.locateOnScreen('./images/enter_button.png', confidence=0.7)
        if enter_button_coords:
            # Divide by 2 for MacOS Retina display scaling
            enter_button_center_coords = ((enter_button_coords[0] + enter_button_coords[2] / 2) / 2, (enter_button_coords[1] + enter_button_coords[3] / 2) / 2)
    except pyautogui.ImageNotFoundException:
        print("No enter button detected!")
        return

    try:
        empty_letter_boxes_unscaled_coords = pyautogui.locateOnScreen('./images/seven_empty_letter_boxes_collection.png', confidence=0.9)
        number_of_empty_letter_boxes = 7
        # More aggressive for 7 letters, more words to get through
        pyautogui.PAUSE = 0.0175
    except pyautogui.ImageNotFoundException:
        try:
            empty_letter_boxes_unscaled_coords = pyautogui.locateOnScreen('./images/six_empty_letter_boxes_collection.png', confidence=0.9)
            number_of_empty_letter_boxes = 6
            # Less aggressive for 6 letters, less words to get through
            pyautogui.PAUSE = 0.0275
        except pyautogui.ImageNotFoundException:
            print("No letter boxes detected!")
            return

    if empty_letter_boxes_unscaled_coords:
        # 2.5% margin on the left and right to avoid detecting off of the iPhone screen
        # Divide by 2 for MacOS Retina display scaling
        screenshot_coordinates = (
            int((empty_letter_boxes_unscaled_coords[0] + empty_letter_boxes_unscaled_coords[2] / 40) / 2),
            int((empty_letter_boxes_unscaled_coords[1] + empty_letter_boxes_unscaled_coords[3]) / 2),
            int((empty_letter_boxes_unscaled_coords[2] - empty_letter_boxes_unscaled_coords[2] / 20) / 2),
            int(empty_letter_boxes_unscaled_coords[3] / 2)
        )
        # Divide by 2 for MacOS Retina display scaling
        individual_letter_boxes_center_coordinates = []
        for i in range(number_of_empty_letter_boxes):
            individual_letter_boxes_center_coordinates.append((
                int((empty_letter_boxes_unscaled_coords[0] + empty_letter_boxes_unscaled_coords[2] / number_of_empty_letter_boxes * i + empty_letter_boxes_unscaled_coords[2] / (number_of_empty_letter_boxes * 2)) / 2),
                int((empty_letter_boxes_unscaled_coords[1] + empty_letter_boxes_unscaled_coords[3] * 1.5) / 2)
            ))

    letters_screenshot = pyautogui.screenshot(region=screenshot_coordinates)
    letters = ocr(letters_screenshot, reader)

    print(f"Detected letters: {letters}")
    if not letters or len(letters) != number_of_empty_letter_boxes:
        print("Incorrect number of letters detected!")
        letters = input("Please enter the letters manually: ").strip().upper()

    possible_words = find_possible_words(letters, word_list)
    display_results(possible_words, letters)

    click_order = convert_word_list_to_click_order(possible_words, letters)
    execute_clicks(click_order, individual_letter_boxes_center_coordinates, enter_button_center_coords)

if __name__ == "__main__":
    main()
