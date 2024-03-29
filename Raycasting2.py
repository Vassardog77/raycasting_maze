###################################################
#
#                 Python Maze Game    
#
###################################################
def main():
# packages
    import pygame
    import sys
    import math
    from pygame import mixer
    make_maze = __import__('maze').make_maze

    # global constants
    SCREEN_HEIGHT = 480
    SCREEN_WIDTH = SCREEN_HEIGHT * 2
    FOV = math.pi / 3
    HALF_FOV = FOV / 2
    CASTED_RAYS = 120 #originally 120
    STEP_ANGLE = FOV / CASTED_RAYS
    SCALE = (SCREEN_WIDTH / 2) / CASTED_RAYS

    # global variables
    player_x = 45
    player_y = 45
    player_angle = math.pi

    # init pygame
    pygame.init()
    mixer.init()
    mixer.music.load('music1.mp3')
    mixer.music.play(-1)

    # create game window
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE) #setting fullscreen

    # set window title
    pygame.display.set_caption('Raycasting')

    # init timer
    clock = pygame.time.Clock()

    # map
    MAP_SIZE = 16
    TILE_SIZE = int((SCREEN_WIDTH / 2) / MAP_SIZE)
    MAX_DEPTH = int(MAP_SIZE * TILE_SIZE)

    MAP = (make_maze())

    print(MAP)

    wall_texture = pygame.image.load("wall_texture2.png").convert()
    background_image = pygame.image.load("background.png").convert()
    win_message = pygame.image.load("win_screen.png").convert()


    # draw map
    def draw_map():
        # loop over map rows
        for row in range(16):
            # loop over map columns
            for col in range(16):
                # calculate square index
                square = row * MAP_SIZE + col

                map_color = (0, 0, 0)
                if MAP[square] == '#':
                    map_color = (200, 200, 200)
                elif MAP[square] == 'f':
                    map_color = (255, 0, 0)
                else:
                    map_color = (100, 100, 100)
                
                # draw map in the game window
                pygame.draw.rect(
                    win,
                    map_color,
                    (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE - 2, TILE_SIZE - 2)
                )

        # draw player on 2D board
        pygame.draw.circle(win, (255, 0, 0), (int(player_x), int(player_y)), 8)
        
        # draw player direction
        pygame.draw.line(win, (0, 255, 0), (player_x, player_y),
                                        (player_x - math.sin(player_angle) * 50,
                                            player_y + math.cos(player_angle) * 50), 3)
        
        # draw player FOV
        pygame.draw.line(win, (0, 255, 0), (player_x, player_y),
                                        (player_x - math.sin(player_angle - HALF_FOV) * 50,
                                            player_y + math.cos(player_angle - HALF_FOV) * 50), 3)
        
        pygame.draw.line(win, (0, 255, 0), (player_x, player_y),
                                        (player_x - math.sin(player_angle + HALF_FOV) * 50,
                                            player_y + math.cos(player_angle + HALF_FOV) * 50), 3)

    # raycasting algorithm
    def cast_rays():
        # define left most angle of FOV
        start_angle = player_angle - HALF_FOV
        
        # loop over casted rays
        for ray in range(CASTED_RAYS):
                    
            # cast ray step by step
            for depth in range(MAX_DEPTH):
                # get ray target coordinates
                target_x = player_x - math.sin(start_angle) * depth
                target_y = player_y + math.cos(start_angle) * depth
                
                # covert target X, Y coordinate to map col, row
                col = int(target_x / TILE_SIZE)
                row = int(target_y / TILE_SIZE)
                
                # calculate map square index
                square = row * MAP_SIZE + col

                # ray hits the condition
                if MAP[square] == '#':
                    # highlight wall that has been hit by a casted ray
                    pygame.draw.rect(win, (0, 255, 0), (col * TILE_SIZE,
                                                        row * TILE_SIZE,
                                                        TILE_SIZE - 2,
                                                        TILE_SIZE - 2))

                    # draw casted ray
                    pygame.draw.line(win, (255, 255, 0), (player_x, player_y), (target_x, target_y))
                    
                    # wall shading
                    color = 255 / (1 + depth * depth * 0.0001)
                    
                    # fix fish eye effect
                    depth *= math.cos(player_angle - start_angle)
                                    
                    # calculate wall height
                    wall_height = 21000 / (depth + 0.0001)
                    
                    # fix stuck at the wall
                    if wall_height > SCREEN_HEIGHT: wall_height = SCREEN_HEIGHT 

                    # draw 3D projection (rectangle by rectangle...)
                    pygame.draw.rect(win, (0, color, 0), (
                        SCREEN_HEIGHT + ray * SCALE,
                        (SCREEN_HEIGHT / 2) - wall_height / 2,
                        SCALE, wall_height))

                    #adding wall textures
                    wall_texture2 = pygame.transform.scale(wall_texture, (SCALE,wall_height))
                    win.blit( wall_texture2, (SCREEN_HEIGHT + ray * SCALE,
                        (SCREEN_HEIGHT / 2) - wall_height / 2))

                    
                    break

            # increment angle by a single step
            start_angle += STEP_ANGLE


    # moving direction
    forward = True

    # game loop
    while True:
        # escape condition
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        
        # covert target X, Y coordinate to map col, row
        col = int(player_x / TILE_SIZE)
        row = int(player_y / TILE_SIZE)
            
        # calculate map square index
        square = row * MAP_SIZE + col

        # player hits the wall (collision detection)
        if MAP[square] == '#':
            if forward:
                player_x -= -math.sin(player_angle) * 5
                player_y -= math.cos(player_angle) * 5
            else:
                player_x += -math.sin(player_angle) * 5
                player_y += math.cos(player_angle) * 5

        #finish line       
        if MAP[square] == 'f':
            win_screen = pygame.transform.scale(win_message, (480,480))
            win.blit(win_screen, (480,0))
            pygame.display.flip()
            main()


        # update 2D background
        pygame.draw.rect(win, (0, 0, 0), (0, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
        
        # update 3D background
        #pygame.draw.rect(win, (0, 0, 0), (480, SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT)) #floor
        #pygame.draw.rect(win, (0, 0, 0), (480, -SCREEN_HEIGHT / 2, SCREEN_HEIGHT, SCREEN_HEIGHT)) #celing

        celing = pygame.transform.scale(background_image, (480,480))
        win.blit(celing, (480,0))



        
        # draw 2D map
        draw_map()
        
        # apply raycasting
        cast_rays()
        
        # get user input
        keys = pygame.key.get_pressed()
        
        # handle user input
        (mouse_x,mouse_y)= pygame.mouse.get_pos()
        if keys[pygame.K_a]: player_angle -= 0.1
        if keys[pygame.K_d]: player_angle += 0.1
        #player_angle = mouse_x/100

        if keys[pygame.K_w]:
            forward = True
            player_x += -math.sin(player_angle) * 5
            player_y += math.cos(player_angle) * 5
        if keys[pygame.K_s]:
            forward = False
            player_x -= -math.sin(player_angle) * 5
            player_y -= math.cos(player_angle) * 5

        # set FPS
        clock.tick(30)

        # display FPS
        fps = str(int(clock.get_fps()))
        
        # pick up the font
        font = pygame.font.SysFont('Monospace Regular', 30)
        
        # create font surface
        fps_surface = font.render(fps, False, (255, 255, 255))
        
        # print FPS to screen
        win.blit(fps_surface, (480, 0))

        # update display
        pygame.display.flip()


main()