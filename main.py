from collections import Counter
import time
import pyautogui
import pytesseract
from PIL import Image, ImageFilter
import numpy as np

def load_word_list(filename="anagrams-words.txt"):
    with open(filename, 'r') as word_list:
        return [line.strip().upper() for line in word_list if line.strip()]

def can_make_word_from_letters(word, letters):
    word_counter = Counter(word)
    letters_counter = Counter(letters)

    for letter, count in word_counter.items():
        if letters_counter[letter] < count:
            return False
    return True

def find_possible_words(letters, word_list):
    letters = letters.upper().replace(" ", "")
    if len(letters) != 7:
        raise ValueError("Please provide exactly 7 letters!")

    possible_words = []
    for word in word_list:
        if can_make_word_from_letters(word, letters):
            possible_words.append(word)

    # Sort by length (longest first), then alphabetically
    possible_words.sort(key=lambda x: (-len(x), x))
    return possible_words

# Convert each word to numbers, 1 being clicking the left-most letter, 7 being clicking the right-most letter
def convert_word_list_to_click_order(word_list, letters):
    pass

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

def main():
    word_list = load_word_list()
    if not word_list:
        return
    start_button_coords = pyautogui.locateOnScreen('./images/start_button.png', confidence=0.7)
    if start_button_coords:
        # Divide by 2 for MacOS Retina display scaling
        start_button_center_coords = ((start_button_coords[0] + start_button_coords[2] / 2) / 2, (start_button_coords[1] + start_button_coords[3] / 2) / 2)
    pyautogui.click(start_button_center_coords, clicks=2, interval=0.2)
    time.sleep(1)

    enter_button_coords = pyautogui.locateOnScreen('./images/enter_button.png', confidence=0.7)
    if enter_button_coords:
        # Divide by 2 for MacOS Retina display scaling
        enter_button_center_coords = ((enter_button_coords[0] + enter_button_coords[2] / 2) / 2, (enter_button_coords[1] + enter_button_coords[3] / 2) / 2)

    empty_letter_boxes_unscaled_coords = pyautogui.locateOnScreen('./images/empty_letter_boxes_collection.png', confidence=0.9)
    if empty_letter_boxes_unscaled_coords:
        # Divide by 2 for MacOS Retina display scaling
        letter_boxes_coordinates = (
            int(empty_letter_boxes_unscaled_coords[0] / 2),
            int((empty_letter_boxes_unscaled_coords[1] + empty_letter_boxes_unscaled_coords[3]) / 2),
            int(empty_letter_boxes_unscaled_coords[2] / 2),
            int(empty_letter_boxes_unscaled_coords[3] / 2)
        )
        # Same as letter_boxes_coordinates but with a 2.5% margin on the left and right to avoid detecting off of the iPhone screen
        screenshot_coordinates = (
            int((empty_letter_boxes_unscaled_coords[0] + empty_letter_boxes_unscaled_coords[2] / 40) / 2),
            int((empty_letter_boxes_unscaled_coords[1] + empty_letter_boxes_unscaled_coords[3]) / 2),
            int((empty_letter_boxes_unscaled_coords[2] - empty_letter_boxes_unscaled_coords[2] / 20) / 2),
            int(empty_letter_boxes_unscaled_coords[3] / 2)
        )
    letters_screenshot = pyautogui.screenshot(region=screenshot_coordinates)

    # Binarize the image
    img_array = np.array(letters_screenshot.convert('L'))
    threshold = 30  # Adjust this value if needed
    img_array = np.where(img_array < threshold, 0, 255).astype(np.uint8)
    binarized_letters = Image.fromarray(img_array, mode='L')

    # Simple OCR for black text
    letters_text = pytesseract.image_to_string(binarized_letters, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    letters = letters_text.strip().replace(' ', '').upper()

    print(f"Detected letters: {letters}")

    possible_words = find_possible_words(letters, word_list)
    display_results(possible_words, letters)

if __name__ == "__main__":
    main()
