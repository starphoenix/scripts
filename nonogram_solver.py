class NonogramBoard:
  
  def __init__(self, rows, columns):
    self.rows = rows
    self.columns = columns
    self.width = len(self.columns)
    self.height = len(self.rows)
    self.grid = [["_" for y in range(self.height)] for x in range(self.width)]
    
  def __str__(self):
    grid_str = ""
    for y in range(self.height):
      row_str = ""
      for x in range(self.width):
        row_str += self.grid[x][y]
      grid_str += row_str
      grid_str += "\n"
    return grid_str

  def get_total(self, list):
    total = sum(list)
    total += len(list) - 1
    return total
    
  def validate(self):
    for row in self.rows:
      if self.get_total(row) > self.width:
        return False
      
    for col in self.columns:
      if self.get_total(col) > self.height:
        return False
    
    return True
    
  def _set_range(
    self, is_row, line, start, count, mark):
      for i in range(count):
        x = start + i if is_row else line
        y = line if is_row else start + i
        cur_mark = self.grid[x][y]
        if cur_mark != "_" and cur_mark != mark:
          raise Exception("Encountered conflict at grid position ({},{})".format(x, y))
        self.grid[x][y] = mark
        
  def _get_line_numbers(self, is_row, line):
    nums = []
    cur_count=0
    line_length = self.width if is_row else self.height
    for i in range(line_length):
      x = i if is_row else line
      y = line if is_row else i
      m = self.grid[x][y]
      if m == "O":
        cur_count += 1
      elif cur_count > 0:
        nums.append(cur_count)
        cur_count = 0
    return nums
    
  def _find_guaranteeds(self, is_row, line, numbers):
    total = self.get_total(numbers)
    line_length = self.width if is_row else self.height
    diff = line_length - total
    if max(numbers) <= diff:
      # No guaranteed cells this line
      return
    cur_idx = 0
    for n in numbers:
      to_fill = n - diff
      if to_fill > 0:
        self._set_range(is_row, line, cur_idx+diff, to_fill, "O")
      cur_idx += n + 1

  def _find_impossible(self, is_row, line, numbers):
    # Reasons a cell may be impossible:
    # 1) Gap is too small to fit the appropriate number in it
    # 2) Cell is too far from the first or last filled cell, assuming we know that that cell belongs to the first or last number
    # Is the first filled cell definitely attributable to the first number?
    line_length = self.width if is_row else self.height
    cur_gap = 0
    first_fits = False
    for i in range(line_length):
      x = i if is_row else line
      y = line if is_row else i
      if self.grid[x][y] == "O":
        break
      elif self.grid[x][y] == "X":
        # Hit a mark, can the current gap fit the first number
        if cur_gap < numbers[0]:
          # First number cannot fit in first gap, these are impossible
          self._set_range(is_row, line, 0, i, "X")
          # Reset gap size, continue searching row
          cur_gap = 0
        else:
          # First number can fit in gap, no impossible cells here
          first_fits = True
          break
      else:
        # Still a blank cell, increase gap size and continue
        cur_gap += 1

    if not first_fits:
      # First doesn't fit



  
  def solve(self):      
    # First find empy, or full rows/columns
    # Rows
    for idx,row in enumerate(self.rows):
      if self.get_total(row) == 0:
        # Empty row, set all to X
        self._set_range(True, idx, 0, self.width, "X")
      elif self.get_total(row) == self.width:
        # Row is full, populate accordingly
        cur_idx = 0
        for n in row:
          self._set_range(True, idx, cur_idx, n, "O")
          cur_idx += n
          if cur_idx < self.width:
            self._set_range(True, idx, cur_idx, 1, "X")
            cur_idx += 1
            
    # Columns
    for idx,col in enumerate(self.columns):
      if self.get_total(col) == 0:
        # Empty column, set all to X
        self._set_range(False, idx, 0, self.height, "X")
      elif self.get_total(col) == self.height:
        # Column is full, populate accordingly
        cur_idx = 0
        for n in col:
          self._set_range(False, idx, cur_idx, n, "O")
          cur_idx += n
          if cur_idx < self.width:
            self._set_range(False, idx, cur_idx, 1, "X")
            cur_idx += 1
    while True:
      for idx, row in enumerate(self.rows):
        self._find_guaranteeds(True, idx, row)
        self._find_impossible(True, idx, row)

      for idx, col in enumerate(self.columns):
        self._find_guaranteeds(False, idx, col)
        self._find_impossible(False, idx, col)

      break
    # Fill guaranteed cells (numbers in a line with a total close enough to the size of the line)
    # Fill other known cells, ones close enough to a boundary (edge or X) that must have others filled based on numbers
    # Find "impossible" cells, ones that cannot be filled due to presence of other fills or Xs


b = NonogramBoard([[5],[0],[1,1,1],[3,1],[2,1]],[[1],[1],[1],[1],[1]])
print("Board: \n{}".format(str(b)))
b.solve()
print("Board: \n{}".format(str(b)))
