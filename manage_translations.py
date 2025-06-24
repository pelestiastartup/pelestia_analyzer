import os
import subprocess

# Directories
TRANSLATIONS_DIR = "translations"
BABEL_CFG = "babel.cfg"
MESSAGES_POT = "messages.pot"

def run_command(command):
    print(f"Running: {command}")
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError:
        print(f"⚠️ Error occurred when running: {command}")

def extract_strings():
    if not os.path.exists(BABEL_CFG):
        print(f"❌ Missing {BABEL_CFG}.")
        return
    run_command(f"python -m babel.messages.frontend extract -F {BABEL_CFG} -o {MESSAGES_POT} .")

def compile_translations():
    if not os.path.exists(TRANSLATIONS_DIR):
        print(f"❌ Missing {TRANSLATIONS_DIR} directory.")
        return
    run_command(f"python -m babel.messages.frontend compile -d {TRANSLATIONS_DIR}")

def init_language(lang_code):
    print(f"Initializing language: {lang_code}")
    run_command(f"python -m babel.messages.frontend init -i {MESSAGES_POT} -d {TRANSLATIONS_DIR} -l {lang_code}")

if __name__ == "__main__":
    print("📚 Pelestia Translation Manager 📚")
    extract_strings()
    
    print("\nDo you want to initialize a new language? (y/n)")
    if input("> ").lower() == 'y':
        lang = input("Enter language code (e.g., 'ar', 'fr', 'en'): ").strip()
        init_language(lang)
    
    print("\nCompiling translations...")
    compile_translations()

    print("\n✅ All done!")