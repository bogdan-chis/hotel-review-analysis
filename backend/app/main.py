import ollama
import json
import os

def load_file_content(filepath):
    """Helper function to read text files."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing required file: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read().strip()

def analyze_reviews_from_files(system_prompt_file, reviews_file):
    try:
        system_instructions = load_file_content(system_prompt_file)
        raw_reviews = load_file_content(reviews_file)

        user_prompt = f"Analyze the following Customer Reviews:\n\n{raw_reviews}"

        response = ollama.chat(
            model='llama3.2:1b',
            messages=[
                {
                    'role' : 'system',
                    'content': system_instructions
                },
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ],
            format='json',
            options={'temperature': 0.1}
        )

        result_dict = json.loads(response['message']['content'])
        return result_dict

    except FileNotFoundError as e:
        print(f"File Error: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: The model did not return valid a JSON.")
    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        return None

if __name__ == "__main__":
    PROMPT_FILE = "system_prompt.txt"
    REVIEWS_FILE = "reviews.txt"

    print ("Analyzing reviews... Please wait.")

    analysis = analyze_reviews_from_files(PROMPT_FILE, REVIEWS_FILE)
    if analysis:
        print("\n--- Extracted Highlights ---")
        for h in analysis.get('highlights', []):
            print(f"• {h}")
            
        print("\n--- Extracted Pain Points ---")
        for p in analysis.get('pain_points', []):
            print(f"• {p}")
