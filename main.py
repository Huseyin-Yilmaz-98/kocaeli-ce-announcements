from Tracker import Tracker
import os

if __name__ == "__main__":
    # change current directory to the file's directory
    if os.path.dirname(__file__)!="":
        try:
            os.chdir(os.path.dirname(__file__))
        except OSError:
            pass
    Tracker().start()
