"""Load SAT quiz JSON files into the database using the quiz resource loader."""
import sys
from pathlib import Path

# Add the academor directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'academor'))

# Setup Django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academor.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("Please ensure all dependencies are installed and the database is configured.")
    sys.exit(1)

from portals.utils.quiz_resource_loader import load_resource_file

def main():
    resources_dir = Path('academor/portals/resources/sat_questions')
    
    # Load SAT Math One
    math_file = resources_dir / 'sat_math_one.json'
    if math_file.exists():
        print(f"Loading SAT Math One from {math_file}...")
        try:
            result = load_resource_file(math_file)
            print(f"Successfully loaded: {result}")
        except Exception as e:
            print(f"Error loading SAT Math One: {e}")
    else:
        print(f"File not found: {math_file}")
    
    # Load SAT Verbal One
    verbal_file = resources_dir / 'sat_verbal_one.json'
    if verbal_file.exists():
        print(f"\nLoading SAT Verbal One from {verbal_file}...")
        try:
            result = load_resource_file(verbal_file)
            print(f"Successfully loaded: {result}")
        except Exception as e:
            print(f"Error loading SAT Verbal One: {e}")
    else:
        print(f"File not found: {verbal_file}")

if __name__ == '__main__':
    main()
