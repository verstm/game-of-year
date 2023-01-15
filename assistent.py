import time
while 1:
    with open('main.py', 'r') as f:
        f1 = f.read()
    with open('main_client.py', 'r') as f:
        f2 = f.read()

    if not f1.replace('game = Main(WIDTH, HEIGHT, screen, FPS, True)', '') == f2.replace('game = Main(WIDTH, HEIGHT, screen, FPS, False)', ''):
        f2 = f1.replace('game = Main(WIDTH, HEIGHT, screen, FPS, True)', 'game = Main(WIDTH, HEIGHT, screen, FPS, False)')
        with open('main_client.py', 'w') as f:
            f.write(f2)
        print('writed')
    else:
        print('not writed')
    time.sleep(5)