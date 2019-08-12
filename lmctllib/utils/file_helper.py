import string
import unicodedata
import logging

logger = logging.getLogger(__name__)

valid_file_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

filename_size_limit = 255

def safe_filename(unsafe_filename):
    # remove spaces
    safe_filename = unsafe_filename.replace(' ','_')
    # valid ascii
    safe_filename = unicodedata.normalize('NFKD', unsafe_filename).encode('ASCII', 'ignore').decode()   
    # keep valid charts 
    safe_filename = ''.join(char for char in safe_filename if char in valid_file_chars)
    if len(safe_filename) > filename_size_limit:
        logger.info("Filename over file name limit {0}, truncating characters. Filename may no longer be unique".format(filename_size_limit))
    return safe_filename[:filename_size_limit] 