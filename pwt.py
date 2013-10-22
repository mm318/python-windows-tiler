# CX_Freeze throws up errors without it
import sys
import re

from pwt.controller import Controller
from singleinstance import Singleinstance

import logging


logging.basicConfig(
	filename='errors.log',
	level=logging.DEBUG,
	format='%(asctime)s - %(levelname)s - %(message)s'
)


if(__name__ == '__main__'):
    #way to assure a singleinstance
    this = Singleinstance()

    if not(this.alreadyrunning()):
        #initialization
        controller = Controller('Python Windows Tiler')
        logging.info('START controller')
        controller.start()

