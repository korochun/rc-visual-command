import pygame
import pygame.camera

pygame.init()
pygame.camera.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame Camera View")
cam = pygame.camera.Camera(0)
cam.start()

while True:
    image = cam.get_image()
    screen.blit(image,(0,0))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cam.stop()
            pygame.quit()
            quit()

pygame.image.frombytes()