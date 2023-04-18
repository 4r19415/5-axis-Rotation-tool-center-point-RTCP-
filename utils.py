class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class state:
    READY = 0
    MOVING = 1

SLIDING_GAIN = 1
ZOOM_GAIN = 50
ROTATION_GAIN = 0.01
DOUBLE_CLICK_DELAY = 350
FPS = 60

WINDOWHEIGHT = 720
WINDOWWIDTH  = 1280
ORIGINEX = -400
ORIGINEY = 500 #-300
ORIGINEZ = 700 #300