import pygame
import random
import json
import requests
import openai
import time

pygame.init()

openai.api_key = ""

WORDS_API_URL = "https://random-word-api.vercel.app/api?words=1"

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (50, 50, 50)
OVERLAY_COLOR = (0, 0, 0, 150)
FONT_LARGE = pygame.font.Font(None, 60)
FONT_MEDIUM = pygame.font.Font(None, 40)
FONT_SMALL = pygame.font.Font(None, 30)

LANGUAGES = {
    "english": {
        "rules": [
            "Welcome to Hangman!",
            "Rules:",
            "1. Guess the word by selecting one letter at a time.",
            "2. You have a limited number of attempts.",
            "3. For every incorrect guess, part of the hangman is drawn.",
            "4. Win by guessing all letters before the hangman is complete.",
        ],
        "select_difficulty": "Select Difficulty Level",
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
        "guess_the_word": "Guess the Word:",
        "guessed_letters": "Guessed Letters:",
        "remaining_attempts": "Remaining Attempts:",
        "win": "You Win!",
        "lose": "You Lose!",
        "the_word_was": "The word was:",
        "play_again": "Play Again",
        "select_language": "Select Language",
    },
    "macedonian": {
        "rules": [
            "Добредојдовте во Бесилка!",
            "Правила:",
            "1. Погодете го зборот избирајќи по една буква.",
            "2. Имате ограничен број обиди.",
            "3. За секоја неточна буква, се црта дел од бесилката.",
            "4. Победете ако ги погодите сите букви пред бесилката да биде завршена.",
        ],
        "select_difficulty": "Изберете тежина",
        "easy": "Лесно",
        "medium": "Средно",
        "hard": "Тешко",
        "guess_the_word": "Погодете го зборот:",
        "guessed_letters": "Погодени букви:",
        "remaining_attempts": "Преостанати обиди:",
        "win": "Победивте!",
        "lose": "Изгубивте!",
        "the_word_was": "Зборот беше:",
        "play_again": "Играј пак",
        "select_language": "Изберете јазик",
    },
}

WORDS = {
    "english": ["python", "hangman", "programming", "challenge"],
    "macedonian": ["компјутер", "програмирање", "занает", "книга"],
}

CATEGORIES = ["Animals", "Technology", "Sports"]

def fetch_word_from_api():
    try:
        response = requests.get(WORDS_API_URL)
        response.raise_for_status()  
        word = response.json()[0]  
        print(f"Fetched word: {word}")  
        return word
    except requests.exceptions.RequestException as e:
        print(f"Error fetching word: {e}")
    return None



def filter_word_with_llm(word, category):
    prompt = f"Does the word '{word}' belong to the category '{category}'? Respond with 'yes' or 'no'."
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
            )
            print(f"OpenAI response: {response}")  # Debugging line
            answer = response['choices'][0]['message']['content'].strip().lower()
            return answer == "yes"

        except openai.error.RateLimitError:
            if attempt < retry_attempts - 1:
                print("Rate limit exceeded, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print("Max retries reached. Could not process request.")
                raise
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            break

#
# def get_word_for_category(category, difficulty):
#     """Fetch and filter a word for the given category and difficulty."""
#     attempts = 0
#     max_retries = 5  # Limit the retries to prevent infinite loops
#     while attempts < max_retries:
#         word = fetch_word_from_api()
#         if not word:
#             attempts += 1
#             continue
#         if filter_word_with_llm(word, category):
#             print(f"Selected word: {word}")
#             return word
#         attempts += 1
#     print("No valid word found after retries.")
#     return None  # Or handle this scenario as needed

def fetch_word_from_llm(category):
    prompt = f"Please generate a word related to the category '{category}'."
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
            )
            word = response['choices'][0]['message']['content'].strip().lower()
            print(f"Generated word: {word}")  # Debugging line
            return word

        except openai.error.RateLimitError:
            if attempt < retry_attempts - 1:
                print("Rate limit exceeded, retrying...")
                time.sleep(2 ** attempt) 
            else:
                print("Max retries reached. Could not process request.")
                raise
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            break
    return None 

def get_word_for_category(category, difficulty):
    """Fetch and filter a word for the given category and difficulty."""
    attempts = 0
    max_retries = 5  
    while attempts < max_retries:
        word = fetch_word_from_llm(category)  
        if not word:
            attempts += 1
            continue
        if filter_word_with_llm(word, category):
            print(f"Selected word: {word}")
            return word
        attempts += 1
    print("No valid word found after retries.")
    return None  

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman")

def select_language():
    screen.fill(LIGHT_GRAY)
    draw_text(LANGUAGES["english"]["select_language"], WIDTH // 2, 50, FONT_LARGE, BLUE, center=True)
    english_button = draw_button("English", WIDTH // 2 - 150, 150, 300, 50, GRAY)
    macedonian_button = draw_button("Македонски", WIDTH // 2 - 150, 250, 300, 50, GRAY)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if english_button.collidepoint(event.pos):
                    return "english"
                if macedonian_button.collidepoint(event.pos):
                    return "macedonian"

def draw_text(text, x, y, font, color=BLACK, center=False):
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=(x, y)) if center else (x, y)
    screen.blit(rendered_text, text_rect)

def draw_hangman(wrong_attempts):
    pygame.draw.line(screen, DARK_GRAY, (150, 500), (250, 500), 5)
    pygame.draw.line(screen, DARK_GRAY, (200, 500), (200, 100), 5)
    pygame.draw.line(screen, DARK_GRAY, (200, 100), (300, 100), 5)
    pygame.draw.line(screen, DARK_GRAY, (300, 100), (300, 150), 5)

    if wrong_attempts > 0:  
        pygame.draw.circle(screen, DARK_GRAY, (300, 175), 25, 5)
    if wrong_attempts > 1: 
        pygame.draw.line(screen, DARK_GRAY, (300, 200), (300, 300), 5)
    if wrong_attempts > 2: 
        pygame.draw.line(screen, DARK_GRAY, (300, 225), (250, 275), 5)
    if wrong_attempts > 3:  
        pygame.draw.line(screen, DARK_GRAY, (300, 225), (350, 275), 5)
    if wrong_attempts > 4:  
        pygame.draw.line(screen, DARK_GRAY, (300, 300), (250, 375), 5)
    if wrong_attempts > 5:  
        pygame.draw.line(screen, DARK_GRAY, (300, 300), (350, 375), 5)

def draw_button(text, x, y, width, height, color, text_color=BLACK):
    pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
    draw_text(text, x + width // 2, y + height // 2, FONT_SMALL, text_color, center=True)
    return pygame.Rect(x, y, width, height)

def draw_overlay_message(message):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))
    draw_text(message, WIDTH // 2, HEIGHT // 2 - 50, FONT_LARGE, RED, center=True)

def display_rules():
    screen.fill(LIGHT_GRAY)
    rules = [
        "Welcome to Hangman!",
        "Rules:",
        "1. Guess the word by selecting one letter at a time.",
        "2. You have a limited number of attempts.",
        "3. For every incorrect guess, part of the hangman is drawn.",
        "4. Win by guessing all letters before the hangman is complete.",
    ]
    y = 50
    for rule in rules:
        draw_text(rule, WIDTH // 2, y, FONT_MEDIUM, DARK_GRAY, center=True)
        y += 50
    draw_text("Press any key to continue...", WIDTH // 2, y + 50, FONT_SMALL, BLUE, center=True)
    pygame.display.flip()
    wait_for_keypress()

def select_difficulty():
    """Allow the player to select the difficulty level."""
    screen.fill(LIGHT_GRAY)
    draw_text("Select Difficulty Level", WIDTH // 2, 50, FONT_LARGE, BLUE, center=True)
    easy_button = draw_button("Easy", WIDTH // 2 - 150, 150, 300, 50, GRAY)
    medium_button = draw_button("Medium", WIDTH // 2 - 150, 250, 300, 50, GRAY)
    hard_button = draw_button("Hard", WIDTH // 2 - 150, 350, 300, 50, GRAY)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    print("Easy difficulty selected") 
                    return 5  # Easy: 5 attempts
                if medium_button.collidepoint(event.pos):
                    print("Medium difficulty selected")
                    return 8  # Medium: 8 attempts
                if hard_button.collidepoint(event.pos):
                    print("Hard difficulty selected")
                    return 10  # Hard: 10 attempts

def wait_for_keypress():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                return

def select_category():
    return random.choice(CATEGORIES)

def main():
    running = True
    clock = pygame.time.Clock()

    language = select_language()
    texts = LANGUAGES[language]
    word_list = WORDS[language]
    # print(f"Word list: {word_list}")  # Debugging line
    # word_to_guess = random.choice(word_list)

    # Display rules
    screen.fill(LIGHT_GRAY)
    y = 50
    for rule in texts["rules"]:
        draw_text(rule, WIDTH // 2, y, FONT_MEDIUM, DARK_GRAY, center=True)
        y += 50
    draw_text("Press any key to continue...", WIDTH // 2, y + 50, FONT_SMALL, BLUE, center=True)
    pygame.display.flip()
    wait_for_keypress()

    max_attempts = select_difficulty()

    # word_to_guess = random.choice(word_list)
    category = select_category()
    # difficulty = select_difficulty()
    # word_to_guess = get_word_for_category(category, max_attempts)
    category = "Technology"
    word_to_guess = get_word_for_category(category, max_attempts)

    guessed_letters = []
    wrong_attempts = 0
    game_over = False

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                if play_again_button.collidepoint(event.pos):
                    return main()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.unicode.isalpha():
                    letter = event.unicode.lower()
                    if letter not in guessed_letters:
                        guessed_letters.append(letter)
                        if letter not in word_to_guess:
                            wrong_attempts += 1

        draw_hangman(wrong_attempts)

        draw_text("Guess the Word:", WIDTH - 400, 50, FONT_LARGE, BLUE)
        display_word = " ".join([letter if letter in guessed_letters else "_" for letter in word_to_guess])
        draw_text(display_word, WIDTH - 300, 150, FONT_LARGE, BLACK)
        draw_text(f"Guessed Letters: {', '.join(guessed_letters)}", WIDTH - 400, 250, FONT_SMALL, BLACK)
        draw_text(f"Remaining Attempts: {max_attempts - wrong_attempts}", WIDTH - 400, 300, FONT_SMALL, BLACK)

        if "_" not in display_word:
            draw_overlay_message("You Win!")
            game_over = True
        elif wrong_attempts >= max_attempts:
            draw_overlay_message("You Lose!")
            draw_text(f"The word was: {word_to_guess}", WIDTH // 2, HEIGHT // 2, FONT_MEDIUM, RED, center=True)
            game_over = True

        if game_over:
            play_again_button = draw_button("Play Again", WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 50, GRAY, BLACK)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
