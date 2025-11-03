import sys
# from lv_gui import *
sys.path.append('/ui')
from utils import *


def main():
    try:
        create_group()
        # load_assets()
        change_route('home')

    except Exception as e:
        print("Error:", e)

if __name__ == "ui":
    event_loop()
    main()