#!/usr/bin/env python3
import random
from enum import Enum

import pygame
from pygame.rect import Rect

SCREEN_RESOLUTION = (800, 600)

COLOR_GRID = (250, 250, 250)
COLOR_UNKNOWN_CELL = (100, 100, 100)
COLOR_BOMB_CELL = (250, 100, 100)
COLOR_SAFE_CELL = (200, 200, 200)
COLOR_FLAGGED_CELL_BG = (100, 100, 100)
COLOR_FLAGGED_CELL_FG = (100, 100, 250)
COLOR_CELL_TEXT = (0, 0, 0)


class CellType(Enum):
  SAFE = 1
  BOMB = 2


class CellStatus(Enum):
  UNKNOWN = 1
  DISCOVERED = 2
  FLAGGED = 3


class Cell:
  def __init__(self, position, cell_type):
    self.position = position
    self.cell_type = cell_type
    self.status = CellStatus.UNKNOWN

  def __repr__(self):
    return "(%s, %s)" % (self.cell_type.name, self.status.name)


class Grid:
  def __init__(self, dimensions, num_bombs, font, cell_size):
    self._dimensions = dimensions
    self._cell_size = cell_size
    self._font = font
    self._grid = []
    cells = []
    for i in range(0, self._dimensions[0]):
      column = []
      self._grid.append(column)
      for j in range(0, self._dimensions[1]):
        column.append(Cell((i, j), CellType.SAFE))
        cells.append((i, j))
    for _ in range(num_bombs):
      bomb_cell = random.choice(cells)
      cells.remove(bomb_cell)
      self._grid[bomb_cell[0]][bomb_cell[1]].cell_type = CellType.BOMB

  def render(self, screen, game_over):

    for i in range(0, self._dimensions[0] + 1):
      x = i * self._cell_size
      pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, self._dimensions[1] * self._cell_size))
    for j in range(0, self._dimensions[1] + 1):
      y = j * self._cell_size
      pygame.draw.line(screen, COLOR_GRID, (0, y), (self._dimensions[0] * self._cell_size, y))

    for i in range(0, self._dimensions[0]):
      for j in range(0, self._dimensions[1]):
        x = i * self._cell_size
        y = j * self._cell_size
        cell = self._grid[i][j]
        if cell.status == CellStatus.UNKNOWN:
          pygame.draw.rect(screen, COLOR_UNKNOWN_CELL, Rect(x + 1, y + 1, self._cell_size - 1, self._cell_size - 1))
        elif cell.status == CellStatus.DISCOVERED:
          if cell.cell_type == CellType.BOMB:
            pygame.draw.rect(screen, COLOR_BOMB_CELL, Rect(x + 1, y + 1, self._cell_size - 1, self._cell_size - 1))
          else:
            pygame.draw.rect(screen, COLOR_SAFE_CELL, Rect(x + 1, y + 1, self._cell_size - 1, self._cell_size - 1))
            num_bomb_neighbours = self._count_bomb_neighbours((i, j))
            if num_bomb_neighbours > 0:
              text = str(num_bomb_neighbours)
              text_pos = (x + self._cell_size // 2 - self._font.size(text)[0] // 2, y )
              screen.blit(self._font.render(text, True, COLOR_CELL_TEXT), text_pos)
        elif cell.status == CellStatus.FLAGGED:
          pygame.draw.rect(screen, COLOR_FLAGGED_CELL_BG, Rect(x + 1, y + 1, self._cell_size - 1, self._cell_size - 1))
          color_fg = COLOR_FLAGGED_CELL_FG
          if game_over and cell.cell_type == CellType.BOMB:
            color_fg = (250, 0, 0)
          pygame.draw.circle(screen, color_fg, (x + self._cell_size // 2, y + self._cell_size // 2),
                             self._cell_size // 4)

  def handle_mouse_click(self, mouse_position):
    x, y = mouse_position
    i = x // self._cell_size
    j = y // self._cell_size
    if self._is_within_grid(i, j):
      print("clicked on cell (%i, %i)" % (i, j))
      cell = self._grid[i][j]
      cell.status = CellStatus.DISCOVERED
      if cell.cell_type == CellType.BOMB:
        print("GAME OVER")
        return True
      count = self._count_bomb_neighbours((i, j))
      if count == 0:
        self._explore_outwards_from(cell)

  def handle_mouse_right_click(self, mouse_position):
    x, y = mouse_position
    i = x // self._cell_size
    j = y // self._cell_size
    if self._is_within_grid(i, j):
      print("right clicked on cell (%i, %i)" % (i, j))
      cell = self._grid[i][j]
      if cell.status == CellStatus.UNKNOWN:
        cell.status = CellStatus.FLAGGED
      elif cell.status == CellStatus.FLAGGED:
        cell.status = CellStatus.UNKNOWN

  def has_player_won(self):
    for i in range(0, self._dimensions[0]):
      for j in range(0, self._dimensions[1]):
        cell = self._grid[i][j]
        if cell.status == CellStatus.UNKNOWN:
          return False
        if cell.status == CellStatus.FLAGGED and cell.cell_type == CellType.SAFE:
          return False
    return True

  def _is_within_grid(self, i, j):
    return 0 <= i < self._dimensions[0] and 0 <= j < self._dimensions[1]

  def _count_bomb_neighbours(self, cell_position):
    count = 0
    for i in range(cell_position[0] - 1, cell_position[0] + 2):
      for j in range(cell_position[1] - 1, cell_position[1] + 2):
        if self._is_within_grid(i, j) and self._grid[i][j].cell_type == CellType.BOMB:
          count += 1
    return count

  def _explore_outwards_from(self, cell):
    to_visit = [cell]
    while to_visit:
      current = to_visit.pop(0).position
      for i in range(current[0] - 1, current[0] + 2):
        for j in range(current[1] - 1, current[1] + 2):
          if self._is_within_grid(i, j):
            neighbour = self._grid[i][j]
            if neighbour.status == CellStatus.UNKNOWN:
              neighbour.status = CellStatus.DISCOVERED
              count = self._count_bomb_neighbours((i, j))
              if count == 0:
                to_visit.append(neighbour)


def main():
  screen = pygame.display.set_mode(SCREEN_RESOLUTION)
  pygame.font.init()
  font = pygame.font.Font('Courier New Bold.ttf', 32)
  grid_size = (20, 15)
  num_bombs = 20
  cell_size = 32
  grid = Grid(grid_size, num_bombs, font, cell_size)

  game_over = False
  while True:

    events = pygame.event.get()
    for event in events:
      if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        exit_game()
      if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
        if event.button == 1:
          game_over = grid.handle_mouse_click(pygame.mouse.get_pos())
        elif event.button == 3:
          grid.handle_mouse_right_click(pygame.mouse.get_pos())

    if not game_over and grid.has_player_won():
      print("YOU WON!")
      game_over = True

    screen.fill((0, 0, 0))

    grid.render(screen, game_over)
    pygame.display.flip()


def exit_game():
  pygame.quit()
  exit(0)


if __name__ == "__main__":
  main()
