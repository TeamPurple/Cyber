import os
import time

interval = 180
while True:
    try:
        os.system('python whatspy.py')
    except:
        pass
    time.sleep(interval)

