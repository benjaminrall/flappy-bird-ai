import pygame, neat, time, os, random  # import all needed modules

pygame.init()  # initialise pygame

# use capitals for constants
WIN_WIDTH = 500  # set window width and height
WIN_HEIGHT = 800

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),  # load bird images
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))  # load pipe image
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))  # load floor image
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))  # load background image
FONT = pygame.font.SysFont("comicsans", 50)


class Bird():
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # how much bird can tilt up when jumping
    ROT_VEL = 20  # how much to rotate on each frame
    ANIMATION_TIME = 5  # how long each bird image will be shown

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # how much tilted
        self.tick_count = 0  # to figure out physics of bird when jumping - time since last jump
        self.vel = 0
        self.height = self.y
        self.img_count = 0  # to know which frame of animation is being shown
        self.img = self.IMGS[0]

    def jump(self):  # for when he flaps upwards
        self.vel = -10.5  # because >y = >down, <y = > up, ergo negative velocity to jump
        self.tick_count = 0
        self.height = self.y  # keep track of where bird originally jumped from

    def move(self):  # called each frame to move bird by velocity
        self.tick_count += 1  # counts each frame since jump
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2  # calculates displacement,how much it moves,creates arc

        if d >= 16:  # terminal velocity
            d = 16
        if d < 0:
            d -= 2  # gives a better upwards thrust - better jump
        self.y += d  # moves by displacement

        if d < 0 or self.y < self.height + 50:  # if moving up or higher than original jump position
            if self.tilt < self.MAX_ROTATION:  # tilt upwards to max rotation
                self.tilt = self.MAX_ROTATION
        else:  # not tilting upwards
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL  # tilts downwards

    def draw(self, win):
        self.img_count += 1  # handles changing frames of the animation - flapping wings
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:  # if nosediving
            self.img = self.IMGS[1]  # stop animation, just go straight
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)  # rotates image, then puts it on the centre
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):  # returns mask - array of all pixels inside an image
        return pygame.mask.from_surface(self.img)  # used for pixel-perfect collision


class Pipe():
    GAP = 200  # gap between pipes
    VEL = 5  # pipe's velocity to the left

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0  # keep track of where top pipe will be drawn
        self.bottom = 0  # and where the bottom pipe will be drawn
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # get top pipe image (flipped)
        self.PIPE_BOTTOM = PIPE_IMG  # get bottom pipe image (normal)

        self.passed = False  # has been passed by bird (for collision and ai purposes)
        self.set_height()

    def set_height(self):  # uses random number height to get both the top and bottom pipe's y
        self.height = random.randrange(50, 450)  # gets random height for pipes
        self.top = self.height - self.PIPE_TOP.get_height()  # gets top pipe y (will be off screen)
        self.bottom = self.height + self.GAP  # gets botton pipe y

    def move(self):
        self.x -= self.VEL  # moves left by subtracting from x

    def draw(self, win):  # draws pipes to window
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):  # handles collision detection between bird and pipes
        bird_mask = bird.get_mask()  # gets mask for bird & 2 pipes
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))  # calculates offset, how far masks are from each other
        bottom_offset = (
            self.x - bird.x, self.bottom - round(bird.y))  # knows how to check pixels up against each other

        b_point = bird_mask.overlap(bottom_mask,
                                    bottom_offset)  # checks for point of overlap between bird and bottom pipe
        t_point = bird_mask.overlap(top_mask, top_offset)  # checks for point of overlap between bird and top pipe

        if t_point or b_point:  # if there is a collision/overlap between a pipe and a bird
            return True  # there was a collision
        return False


class Base():
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0  # x's for 2 bases, which will be used to have a seemingly infinite base
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL  # moves both bases
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:  # checks if one base is off screen,
            self.x1 = self.x2 + self.WIDTH  # cycle it back to the other side
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score):  # draws & updates window
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)

    text = FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0
    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y,
                                       abs(bird.y - pipes[pipe_ind].height),
                                       abs(bird.y - pipes[pipe_ind].bottom)))
            if output[0] > 0.5:
                bird.jump()

        rem = []
        add_pipe = False
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)
            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
        for r in rem:
            pipes.remove(r)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        if score > 100:
            break

        base.move()
        draw_window(win, birds, pipes, base, score)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 50)
    print(winner)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
