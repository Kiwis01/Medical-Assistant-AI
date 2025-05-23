# add all imports here

#Logginf
import logging

# Data reading
import json
from pathlib import Path
import re
import os
import signal
import datetime

# api dependencies
import requests

# OpenCV
import cv2

# Numpy
import numpy as np  

# Common utils
from utils.common_utils import *

# Database
from werkzeug.security import generate_password_hash, check_password_hash

from flask import current_app