from catpic import CatpicEncoder
encoder = CatpicEncoder(basis=(2, 2))
meow = encoder.encode_image('test.jpg', width=80)
print(meow)
