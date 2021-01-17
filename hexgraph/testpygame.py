import sys, pygame
pygame.init()

size = width, height = 320, 240
speed = [2, 2]
black = 0, 0, 0

#screen = pygame.display.set_mode(size)

ball = pygame.image.load("world_default_medium.jpg")
ballrect = ball.get_rect()
ballsize = ballrect.size
print ("size = {}".format(ballsize))

w, h = ballsize
ball = pygame.transform.scale(ball, (int(w * 1.30), int(h * 1.30)))
ballrect = ball.get_rect()
ballsize = ballrect.size
print ("size = {}".format(ballsize))

screen = pygame.display.set_mode(ballsize)
screen.fill(black)
screen.blit(ball, ballrect)
SQRT_3 = 3**0.5
HEX_WIDTH = 36
HEX_HEIGHT = HEX_WIDTH * 2 / SQRT_3

#hex_width = 36
#x = int(hex_width / 2)
#y = hex_width * 2 / sqrt_3
#y = int(y / 2)
BLACK = (0, 0, 0)

#
# Convert a hex coordinate to a point coordinate
# Where the point is located in the center of the hex
#
# Assumes pointy up orientation with the top row flush
# to the left.
#
def hex_to_point(hex_x, hex_y):
    x = hex_x * HEX_WIDTH + 0.5 * HEX_WIDTH * (hex_y & 1)
    y = hex_y * HEX_HEIGHT * 3 / 4
    x += HEX_WIDTH / 2
    y += HEX_HEIGHT / 2
    return (int(x), int(y))


def is_odd(num):
    return bool(num & 1)

#for hex_x in range(28):
#    for hex_y in range(21):
#        (x, y) = hex_to_point(hex_x, hex_y)
#        pygame.draw.circle(screen, BLACK, (x, y), 10, 0)


pygame.display.flip()
input("press key to continue")

#exit(0)
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()