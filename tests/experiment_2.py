with open('my_text_file.txt', 'r+') as f:
    f.read()
    f.seek(0)
    f.write('hi')