import pygame
import os
import random
import neat

ai_playing = True
generation = 0

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800

IMAGE_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGE_FLOOR = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGE_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))
IMAGES_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
]

pygame.font.init()
FONT = pygame.font.SysFont('arial', 50)

class Bird:
    IMGS = IMAGES_BIRD
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.velocity = 0
        self.height = self.y
        self.tick = 0
        self.image = self.IMGS[0]
        self.count_image = 0
        
    def jump(self):
        self.velocity = -10.5
        self.tick = 0
        self.height = self.y

    def move(self):
        self.tick += 1
        displacement = 1.5 * (self.tick ** 2) + self.velocity * self.tick

        if displacement >= 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < (self.height + 50):
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        self.count_image += 1
        if self.count_image < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.count_image < self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1]
        elif self.count_image < self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2]
        elif self.count_image < self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1]
        elif self.count_image < self.ANIMATION_TIME * 5:
            self.image = self.IMGS[0]
        
        self.count_image = 0

        if self.tilt <= -80:
            self.image = self.IMGS[1]
            self.count_image = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        rectangle = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0
        self.base = 0
        self.PIPE_TOP = pygame.transform.flip(IMAGE_PIPE, False, True)
        self.PIPE_BASE = IMAGE_PIPE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.base = self.height + self.DISTANCE

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BASE, (self.x, self.base))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        base_mask = pygame.mask.from_surface(self.PIPE_BASE)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        base_offset = (self.x - bird.x, self.base - round(bird.y))

        top_point = bird_mask.overlap(top_mask, top_offset)
        base_point = bird_mask.overlap(base_mask, base_offset)

        if top_point or base_point:
            return True
        return False

class Floor:
    VELOCITY = 5
    WIDTH = IMAGE_FLOOR.get_width()
    IMAGE = IMAGE_FLOOR

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMAGE, (self.x1, self.y))
        window.blit(self.IMAGE, (self.x2, self.y))

def draw_window(window, birds, pipes, floor, score):
    window.blit(IMAGE_BACKGROUND, (0, 0))

    for bird in birds:
        bird.draw(window)

    for pipe in pipes:
        pipe.draw(window)
    
    text = FONT.render(f'Score: {score}', 1, (255, 255, 255))
    window.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    if ai_playing:
        text = FONT.render(f'Generation: {generation}', 1, (255, 255, 255))
        window.blit(text, (10, 10))

    floor.draw(window)

    pygame.display.update()

def main(genomas, config):
    global generation
    generation += 1

    if ai_playing:
        nets = []
        list_genomas = []
        birds = []

        for _, genoma in genomas:
            net = neat.nn.FeedForwardNetwork.create(genoma, config)
            nets.append(net)
            genoma.fitness = 0
            list_genomas.append(genoma)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    score = 0
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if not ai_playing:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    for bird in birds:
                        bird.jump()
        
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            rodando = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            list_genomas[i].fitness += 0.1
            output = nets[i].activate((bird.y, abs(bird.y - pipes[pipe_index].height), abs(bird.y - pipes[pipe_index].base)))

            if output[0] > 0.5:
                bird.jump()
            
        floor.move()

        add_pipe = False
        remove_pipe = []
        for pipe in pipes:
            for i, bird in enumerate (birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        list_genomas[i].fitness -= 1
                        list_genomas.pop(i)
                        nets.pop(i)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipe.append(pipe)

        if add_pipe:
            score += 1
            pipes.append(Pipe(600))
            for genoma in list_genomas:
                genoma.fitness += 5

        for pipe in remove_pipe:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if bird.y + bird.image.get_height() >= floor.y or bird.y < 0:
                birds.pop(i)
                if ai_playing:
                    list_genomas.pop(i)
                    nets.pop(i)


        draw_window(window, birds, pipes, floor, score)


def run(path_config):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, path_config)
    
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    
    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    path_config = os.path.join(path, 'config_ia.txt')
    run(path_config)