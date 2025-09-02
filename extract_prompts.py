# Extracts prompts from PNG images recursively from an 'input' directory.
# Saves prompts to individual text files and/or a concatenated file.

import os
from PIL import Image

# --- Configuration ---
SAVE_INDIVIDUAL_FILES = True            # Save a .txt file for each image with its prompt.
CONCATENATE_PROMPTS = True              # Create a single prompts.txt with all prompts.
REMOVE_NEWLINES_PER_PROMPT = True       # For each prompt, remove newlines to make it a single line.
STRIP_EMPTY_LINES_FROM_OUTPUT = True    # In prompts.txt, remove empty lines that might result from images without prompts.


def extract_prompt(image_path):
    try:
        with Image.open(image_path) as im:
            info = im.info
            # Change this key if your prompt is stored elsewhere.
            if "parameters" in info:
                prompt_text = info["parameters"]
                
                # Remove negative prompt if present
                if "Negative prompt:" in prompt_text:
                    prompt_text = prompt_text.split("Negative prompt:")[0].strip()
                
                # Remove settings if present (start at "Steps:")
                if "Steps:" in prompt_text:
                    prompt_text = prompt_text.split("Steps:")[0].strip()

                if REMOVE_NEWLINES_PER_PROMPT:
                    # Join multi-line prompts into one paragraph
                    prompt_text = " ".join(prompt_text.splitlines()).strip()
                else:
                    prompt_text = prompt_text.strip()

                return prompt_text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
    return None

def main():
    input_folder = "input"
    output_file = "prompts.txt"
    all_prompts = []
    image_count = 0
    no_prompt_count = 0
    processed_folders = set()

    if not os.path.isdir(input_folder):
        print(f"Error: Input directory '{input_folder}' not found.")
        return

    print(f"Scanning for images in '{input_folder}'...")

    for root, _, files in os.walk(input_folder):
        folder_has_images = False
        for file_name in files:
            if file_name.lower().endswith(".png"):
                if not folder_has_images:
                    processed_folders.add(root)
                    folder_has_images = True
                
                image_count += 1
                full_path = os.path.join(root, file_name)
                prompt = extract_prompt(full_path)
                if prompt:
                    all_prompts.append(prompt)
                    if SAVE_INDIVIDUAL_FILES:
                        base_name = os.path.splitext(full_path)[0]
                        with open(base_name + ".txt", "w", encoding="utf-8") as f:
                            f.write(prompt)
                else:
                    no_prompt_count += 1
    
    print("\n--- Scan Complete ---")
    print(f"Folders scanned: {len(processed_folders)}")
    for folder in sorted(list(processed_folders)):
        print(f" - {folder}")
    print(f"Total images found: {image_count}")
    print(f"Prompts found: {len(all_prompts)}")
    print(f"Images without prompts: {no_prompt_count}")
    print("---------------------\n")


    if CONCATENATE_PROMPTS:
        prompts_to_write = all_prompts
        if STRIP_EMPTY_LINES_FROM_OUTPUT:
            prompts_to_write = [p for p in all_prompts if p.strip()]
            
        with open(output_file, "w", encoding="utf-8") as f:
            for prompt in prompts_to_write:
                f.write(prompt + "\n")
        print(f"Saved {len(prompts_to_write)} prompts to {output_file}")
    
    if SAVE_INDIVIDUAL_FILES:
        print(f"Saved {len(all_prompts)} individual prompt files.")

    if not CONCATENATE_PROMPTS and not SAVE_INDIVIDUAL_FILES:
        print("No output files were saved (check configuration).")


if __name__ == "__main__":
    main()
