import pygame as pg


bg_surface = pg.Surface((640, 480), pg.SRCALPHA)
pg.draw.lines(
    bg_surface, (30, 90, 200), True,
    ((60, 130), (300, 50), (600, 200), (400, 400), (150, 300)),
    12)
triangle_surface = pg.Surface((60, 60), pg.SRCALPHA)
pg.draw.polygon(triangle_surface, (160, 250, 0), ((30, 0), (60, 60), (0, 60)))


def main():
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()

    bg_mask = pg.mask.from_surface(bg_surface)
    triangle_mask = pg.mask.from_surface(triangle_surface)

    bg_rect = bg_surface.get_rect(center=(320, 240))
    triangle_rect = triangle_surface.get_rect(center=(0, 0))

    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEMOTION:
                triangle_rect.center = event.pos

        offset_x = triangle_rect.x - bg_rect.x
        offset_y = triangle_rect.y - bg_rect.y

        overlap = bg_mask.overlap(triangle_mask, (offset_x, offset_y))
        if overlap:
            print('The two masks overlap!', overlap)

        screen.fill((30, 30, 30))
        screen.blit(bg_surface, bg_rect)
        screen.blit(triangle_surface, triangle_rect)

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()