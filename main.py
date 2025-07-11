from collections import Counter
import time

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
    print("GamePigeon Anagrams Bot")
    print("=" * 30)
    
    # Load word list
    print("Loading word list...")
    start_time = time.time()
    word_list = load_word_list()
    load_time = time.time() - start_time
    
    if not word_list:
        return
    
    print(f"Loaded {len(word_list):,} words in {load_time:.2f} seconds")
    
    while True:
        print("\nEnter 7 letters (or 'quit' to exit):")
        letters = input("> ").strip()
        
        if letters.lower() == 'quit':
            print("Goodbye!")
            break
        
        if len(letters.replace(" ", "")) != 7:
            print("Please enter exactly 7 letters.")
            continue
        
        if not letters.replace(" ", "").isalpha():
            print("Please enter only letters.")
            continue
        
        # Find possible words
        start_time = time.time()
        possible_words = find_possible_words(letters, word_list)
        search_time = time.time() - start_time
        
        # Display results
        display_results(possible_words, letters)
        print(f"\nSearch completed in {search_time:.3f} seconds")

if __name__ == "__main__":
    main()
