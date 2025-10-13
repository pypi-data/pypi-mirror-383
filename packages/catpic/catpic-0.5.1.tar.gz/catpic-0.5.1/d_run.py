# test_full.py
from catpic import CatpicEncoder, CatpicDecoder

# Encode
encoder = CatpicEncoder(basis=(2, 2))
meow = encoder.encode_image('test.jpg', width=80)

# Decode and display
decoder = CatpicDecoder()
decoder.display(meow)
