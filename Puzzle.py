import pygame
import sys
import random
from helper import *
import math

# Initialize Pygame
pygame.init()

level = Level.level_path


def isOverlapImagePieces(pieces):
    count = 0
    for all in pieces:
        if all.dragging:
            count += 1
        if count > 0:
            return True
    return False


def isFreeSpaceToFitImagePiece(pieces, box_center):
    for all in pieces:
        if all.rect.center == box_center:
            return False
    return True


def puzzle11():
    box_size = 50
    picture = []
    for i in range(9):
        picture.append(loadimages(f"Images/Gate_Puzzle/{i}.png", (box_size, box_size)))
    bg = loadimages(f"Images/Gate_Puzzle/bg.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
    frame = loadimages(f"Images/Gate_Puzzle/Frame.png", (170, 170))
    frame_pos = (90, 40)

    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

    # Set up the screen
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Number Puzzle")
    frame_num = 3

    class DraggablePiece:
        def __init__(self, posX, posY, x, y, size, index, img):
            self.x = x
            self.y = y
            self.posX = posX
            self.posY = posY
            self.img = img
            self.dragging = False
            self.size = size
            self.actualIndex = index
            self.placedIndex = 0
            self.rect = pygame.Rect(
                self.x + self.posX, self.y + self.posY, self.size, self.size
            )

        def draw(self):
            SCREEN.blit(self.img, self.rect)

        def update(self):
            if self.dragging:
                self.rect.center = pygame.mouse.get_pos()

    # Define class for draggable pieces
    def check_repeat(arr, i, j):
        for all in arr:
            if all["i"] == i and all["j"] == j:
                return True

        return False

    def random_indexContainig_array_generator(row, col, piece_num):
        arr = []
        img_piece = []
        while len(arr) != piece_num:
            i = random.randint(0, row)
            j = random.randint(0, col)
            if len(arr) <= 0:
                arr.append({"i": i, "j": j})
            else:
                if not check_repeat(arr, i, j):

                    arr.append({"i": i, "j": j})

        return arr

    pos_arr = random_indexContainig_array_generator(3, 9, 9)
    img_piece = []
    posX = 100
    posY = 50
    for i, all in enumerate(pos_arr):
        img_piece.append(
            DraggablePiece(
                50,
                300,
                all["j"] * box_size,
                all["i"] * box_size,
                box_size,
                i,
                picture[i],
            )
        )

    def draw_frame(posX, posY, size, frame_num):
        check = 1
        for i in range(0, frame_num):
            for j in range(0, frame_num):
                x, y = j * size, i * size
                index = i * frame_num + j
                if img_piece[index].placedIndex != index:
                    check = 0

                pygame.draw.rect(
                    screen, (0, 0, 0), (posX + x, posY + y, box_size, box_size), 1
                )
        return check

    def draw_piece_container(posX, posY, size, arr):
        for i in range(0, 4):
            for j in range(0, 10):
                x, y = j * size, i * size
                pygame.draw.rect(
                    screen, (0, 0, 0), (posX + x, posY + y, box_size, box_size), 1
                )
        for all in arr:

            all.draw()
            all.update()

    while True:
        SCREEN.blit(bg, (0, 0))
        SCREEN.blit(frame, frame_pos)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for piece in img_piece:
                    if piece.rect.collidepoint(event.pos):
                        piece.dragging = (
                            False if isOverlapImagePieces(img_piece) else True
                        )
            elif event.type == pygame.MOUSEBUTTONUP:
                for piece in img_piece:
                    if piece.dragging:
                        piece.dragging = False
                        for i in range(0, frame_num):
                            for j in range(0, frame_num):
                                x, y = j * box_size, i * box_size
                                rct = pygame.Rect(
                                    posX + x, posY + y, box_size, box_size
                                )

                                if piece.rect.colliderect(rct):
                                    dist = math.sqrt(
                                        math.pow(
                                            (piece.rect.center[0] - rct.center[0]), 2
                                        )
                                        + math.pow(
                                            (piece.rect.center[1] - rct.center[1]), 2
                                        )
                                    )

                                    if dist < 15 and isFreeSpaceToFitImagePiece(
                                        img_piece, rct.center
                                    ):
                                        piece.rect.center = rct.center
                                        piece.placedIndex = i * frame_num + j

        win = draw_frame(100, 50, box_size, 3)
        draw_piece_container(50, 300, box_size, img_piece)
        win = True
        if win:
            print("win")
            switch_level()
            print(len(Level.Enemies_array))
            break
        pygame.display.flip()
    return True


# puzzle()
