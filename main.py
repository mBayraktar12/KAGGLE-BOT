import os
import json
import re
import time
import requests
from kaggle import api

# File paths for configuration and for storing the best score
CONFIG_FILE = "config.json"
BEST_SCORE_FILE = "best_score.txt"

def load_config(filename):
    """
    Loads configuration from a JSON file.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Config file '{filename}' not found.")
    with open(filename, "r") as f:
        return json.load(f)

# Load configuration from the external file
config = load_config(CONFIG_FILE)
COMPETITION = config.get("COMPETITION", "drawing-with-llms")
TELEGRAM_BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = config.get("TELEGRAM_CHAT_ID")

def get_best_score(competition):
    """
    Retrieves kernels for the given competition, sorted by descending score.
    If the kernel object lacks a direct score attribute, this function attempts
    to extract the score from the title (e.g., "[LB 0.694] ...").
    """
    try:
        kernels = api.kernels_list(
            competition=competition,
            sort_by="scoreDescending",  # Valid options include 'scoreDescending'
            language="python",
            output_type="all"           # Valid options: 'all', 'visualization', 'data'
        )
        
        if not kernels:
            print("No kernels found for competition:", competition)
            return None, None
        
        # Take the top kernel (expected to have the highest score)
        best_kernel = kernels[0]
        print("Top kernel attributes:", best_kernel.__dict__)
        
        # Attempt to get the score from known attributes
        best_score = getattr(best_kernel, "public_score", None) or getattr(best_kernel, "score", None)
        best_title = best_kernel.title
        
        # If score isn't available, try to parse it from the title using regex.
        if best_score is None:
            match = re.search(r"\[LB\s*([0-9]*\.?[0-9]+)\]", best_title)
            if match:
                best_score = float(match.group(1))
                print(f"Extracted score {best_score} from title.")
            else:
                print("No score found for the top kernel.")
                return None, None
        
        return best_score, best_title
    except Exception as e:
        print("Error retrieving kernels:", e)
        return None, None

def send_telegram_message(bot_token, chat_id, message):
    """
    Sends a message to the specified Telegram chat using the bot token.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print("Failed to send message:", response.text)
    except Exception as e:
        print("Error sending Telegram message:", e)

def load_stored_score(filename):
    """
    Loads the stored best score from a file.
    """
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return float(f.read().strip())
        except Exception as e:
            print("Error reading stored score:", e)
    return None

def save_best_score(filename, score):
    """
    Saves the best score to a file.
    """
    try:
        with open(filename, "w") as f:
            f.write(str(score))
    except Exception as e:
        print("Error saving best score:", e)

def main():
    # Retrieve the current best score from Kaggle
    current_best_score, current_best_title = get_best_score(COMPETITION)
    
    if current_best_score is None:
        print("Unable to retrieve a valid best score. Exiting current iteration.")
        return
    
    print(f"Current best kernel: {current_best_title} with score {current_best_score}")
    
    # Load the previously stored best score
    stored_best_score = load_stored_score(BEST_SCORE_FILE)
    
    if stored_best_score is None:
        print("No stored best score found. Saving the current best score.")
        save_best_score(BEST_SCORE_FILE, current_best_score)
    else:
        print(f"Previously stored best score: {stored_best_score}")
    
    # If a new best score is detected, send a Telegram notification.
    if stored_best_score is None or current_best_score > stored_best_score:
        message = (f"New best kernel published!\n"
                   f"Title: {current_best_title}\n"
                   f"Score: {current_best_score}")
        send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message)
        save_best_score(BEST_SCORE_FILE, current_best_score)
    else:
        print("No new best score. No notification sent.")

def continuous_check(interval_seconds=3600):
    """
    Continuously checks for a new best kernel every interval_seconds seconds.
    """
    while True:
        try:
            main()
        except Exception as e:
            print("Error in main loop:", e)
        print(f"Waiting {interval_seconds} seconds before next check...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    continuous_check()
