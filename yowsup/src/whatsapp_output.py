import os
import sys

def write_available(phone_number, pull_time, last_online):
	f = open(phone_number, 'a')
	f.write(pull_time + ',' + last_online + '\n')
	f.close()
