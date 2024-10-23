import subprocess


def run_tailwind_watch():
    """
    Runs TailwindCSS in watch mode for automatic recompilation using global installation.
    """
    command = [
        'tailwindcss',  # Use the globally installed TailwindCSS
        '-i', './static/css/input.css',  # Input CSS file
        '-o', './static/css/output.css',  # Output CSS file
        '--watch'
    ]
    try:
        subprocess.run(command, check=True)
        print('TailwindCSS watcher started.')
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running TailwindCSS: {e}")
    except FileNotFoundError:
        print("TailwindCSS executable not found. Please ensure it is installed globally.")

run_tailwind_watch()
