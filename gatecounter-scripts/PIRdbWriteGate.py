#!/usr/bin/python3
import collections
import logging
import subprocess
import sys

from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor, CancelledError, wait
from datetime import datetime
from queue import SimpleQueue

import RPi.GPIO as GPIO

from sqlalchemy import Column, DateTime, Integer, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

log = logging.getLogger("sqlalchemy")
info = logging.StreamHandler(sys.stdout)
info.addFilter(lambda x: x.levelno <= logging.WARNING)
errors = logging.StreamHandler(sys.stderr)
errors.addFilter(lambda x: x.levelno >= logging.ERROR)
log.setLevel(logging.DEBUG)
log.addHandler(info)
log.addHandler(errors)


Base = declarative_base()

class PIR_Detection(Base):
    __tablename__ = "PIRSTATS"

    timestamp = Column('timestamp', DateTime, nullable=False, primary_key=True)
    count = Column('count', Integer, nullable=False)


Detection=collections.namedtuple("Detection", ['timestamp','count'])

class PIRgate:
    def __init__(self, hostname, username, password, database):
        # Set RPi GPIO Mode
        GPIO.setmode(GPIO.BCM)

        # Setup GPIO in and out pins
        self.PIR_PIN = 7
        GPIO.setup(self.PIR_PIN, GPIO.IN)
        # End GPIO setup
        self._pool=ThreadPoolExecutor()
        self._detection_queue=SimpleQueue()
        if not hostname:
            stdout,stderr = subprocess.Popen(['docker',
                                              'inspect',
                                              '-f',
                                              "'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'",
                                              'gatecounter-db'],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.STDOUT).communicate()
            host = stdout.decode().strip()
        else:
            host = hostname
        self.db_engine = create_engine(f"mysql://{username}:{password}@{host}/{database}")
        Base.metadata.create_all(bind=self.db_engine)
        self._session_factory = sessionmaker(bind=self.db_engine)
        self.Session = scoped_session(self._session_factory)

    def start(self):
        GPIO.add_event_detect(self.PIR_PIN, GPIO.RISING, callback=lambda c: self._detection_queue.put(Detection(datetime.now(),1)))
        with self._pool:
            try:
                self.db_writer = self._pool.submit(self.write_to_db)
                wait([self.db_writer])
            except KeyboardInterrupt:
                print("\nCtrl-C pressed cleaning up GPIO")
                raise
            finally:
                GPIO.cleanup()

    def write_to_db(self):
        while True:
            try:
                detection = self._detection_queue.get()
                session = self.Session()
                session.add(PIR_Detection(timestamp=detection.timestamp, count=detection.count))
            except KeyboardInterrupt:
                session.rollback()
                raise
            except:
                session.rollback()
                self._detection_queue.put(detection) #return detection to queue to try again
            else:
                session.commit()
            finally:
                session.remove()

if __name__ == "__main__":
    parser = ArgumentParser(description="Begin PIR detections")
    parser.add_argument("-H", "--hostname",default="")
    parser.add_argument("-d", "--database",default="gatecounter")
    parser.add_argument("-u", "--username", required=True)
    parser.add_argument("-p", "--password", required=True)
    if sys.argv[0].startswith("python"):
        args = parser.parse_args(sys.argv[2:])
    else:
        args = parser.parse_args(sys.argv[1:])
    if not args.hostname:
        stdout,stderr = subprocess.Popen(['docker',
                                          'inspect',
                                          '-f',
                                          "'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'",
                                          'gatecounter-db'],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT).communicate()
        host = stdout.decode().strip()
    else:
        host = args.hostname
    try:
        PIRgate(args.hostname, args.username, args.password, args.database).start()
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        print("\nProblem connecting to the database.  Check your credentials and try again \n")
        sys.exit(2)

