from catpic import CatpicEncoder, CatpicDecoder

# Test BASIS 2,4 (ultra quality)
encoder = CatpicEncoder()
meow = encoder.encode_image('test.jpg', width=80)

decoder = CatpicDecoder()
decoder.display(meow)
