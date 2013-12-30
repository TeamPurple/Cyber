import os
import time

interval = 180
while True:
    time.sleep(interval)
    try:
        os.system('python whatspy.py')
    except:
        pass


