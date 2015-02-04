"""
Python Codec Proxy
"""
import imp
from os import path

# Set this to the folder where your codecs are stored.
CODECS_DIR = path.expandvars("$sarkCodecs")

# Load the codecs based on the filename of the proxy
name = __name__.split(".")[-1]

# Force the use of `.py` files as trying to load `.pyc` by filename
# makes Python try and load it as a `.py` file.
codec_filename = name + ".py"
codec_path = path.join(CODECS_DIR, codec_filename)

codec = imp.load_source(__name__, codec_path)

# Export the codec's entry
getregentry = codec.getregentry