# Written By Johnathan Cintron and Devlyn Courtier for the HCCC Library

#!/usr/bin/python

import sys
import MySQLdb
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
from getpass import getpass
from multiprocessing import Queue
from concurrent.futures import ProcessPoolExecutor, CancelledError, wait

class PIRgate:
	def __init__(self, hostname, username, password, database):
		# Set RPi GPIO Mode
		GPIO.setmode(GPIO.BCM)

		# Setup GPIO in and out pins
		self.PIR_PIN = 7
		GPIO.setup(self.PIR_PIN, GPIO.IN)
		# End GPIO setup
		self.counts=Queue()
		self._pool=ProcessPoolExecutor()

	def start(self):
		try:
			self.event_listener = self._pool.submit(self.listen_for_events)
			self.db_writer = self._pool.submit(self.write_to_db, hostname, username, password, database)
		except KeyboardInterrupt:
			print("\nCtrl-C pressed cleaning up GPIO")
			self.event_listener.cancel()
			self.db_writer.cancel()
			GPIO.cleanup()
		finally:
			wait([self.event_listener,self.db_writer])
			GPIO.cleanup()

	def listen_for_events(self):
		count = 0
		while True:
			try:
				if GPIO.input(self.PIR_PIN):
					count += 1
				curr_date = datetime.now()
				if (curr_date.minute % 10 == 0) and (curr_date.second == 0):
					self.counts.put_nowait((curr_date,count))
					count = 0
			except (KeyboardInterrupt,CancelledError):
				break


	def write_to_db(self, hostname, username, password, database):
		while True:
			try:
				time, count = self.counts.get()
				with MySQLdb.connect(hostname,username,password,database) as db:
					try:
						db.cursor().execute("INSERT INTO PIRSTATS (datetime, gatecount) VALUES ('%s', '%d')" % (time.isoformat(' '), count))
					except (KeyboardInterrupt,CancelledError):
						db.rollback()
						break
					except:
						db.rollback()
						self.counts.put(time,count) #put the data back in queue to try writing it again
					else:
						db.commit()
					finally:
						db.close()
			except (KeyboardInterrupt,CancelledError):
				break

if __name__ == "__main__":
	while True:
		try:
			hostname = input("DB Hostname: ")
			database = input("Database: ")
			username = input("Username: ")
			password = getpass()
			#just check the credentials by connecting to the db and closing
			MySQLdb.connect(hostname, username, password, database).close()
		except KeyboardInterrupt:
			sys.exit(1)
		except:
			print("\nProblem connecting to the database.  Check your credentials and try again \n")
			continue
		else:
			break
	PIRgate(hostname, username, password, database).start()