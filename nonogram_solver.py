import numpy as np

def print_array(array):
  mapping = {
    "float": lambda x: "_" if (x == 0) else ("■" if (x == 1) else "X")
  }
  return np.array2string(array, None, None, None, "|", "", formatter=mapping)

class NonogramBoard:
  
  def __init__(self, rows, columns):
    self.rows = rows
    self.columns = columns
    self.width = len(self.rows)
    self.height = len(self.columns)
    print("Width: {} Height: {}".format(self.width, self.height))
#    self.grid = [["_" for y in range(self.height)] for x in range(self.width)]
    self.board = np.zeros((self.width,self.height))
    
  # Mapping: 0 = _, 1 = ■, -1 = X
  def __str__(self):
    mapping = {
      "float": lambda x: "_" if (x == 0) else ("■" if (x == 1) else "X")
    }
    return np.array2string(self.board, None, None, None, "|", "", formatter=mapping)

  # Returns the sum of the clues in a given line plus the spacers between them.
  def get_clues_total(self, list):
    total = sum(list)
    total += len(list) - 1
    return total

  # Checks if the given clues for a board are valid.
  def validate(self):
    for row in self.rows:
      if self.get_clues_total(row) > self.width:
        return False
      
    for col in self.columns:
      if self.get_clues_total(col) > self.height:
        return False
    
    return True

  # Sets the range Start -> Start+Count to the given Mark on the given Line. Mark must be a float, Line is expected to be a 1D numpy array
  def _mark_range(self, line, start, count, mark):
    line[start:start+count] = mark

  #Sets the provided range in the grid to the provided mark.
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

  # "Guaranteeds" are cells that must be filled due to overlap in possible placement of clues.
  def _fill_guaranteeds(self, line, clues):
    total = self.get_clues_total(clues)
    diff = len(line) - total
    if max(clues) <= diff:
      #No overlaps, so no guaranteed cells.
      return
    cur_idx = 0
    for clue in clues:
      overlap = clue - diff
      if overlap > 0:
        self._mark_range(line, cur_idx+diff, overlap, 1)
      cur_idx += clue + 1
    
  def _find_guaranteeds(self, is_row, line, numbers):
    total = self.get_clues_total(numbers)
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
      
  def _fill_impossible(self, line, clues):
    cur_gap = 0
    first_fits = False
    for i in range(len(line)):
      if line[i] == 1:
        break
      elif line[i] ==  -1:
        if cur_gap < clues[0]:
          self._mark_range(line, 0, i, -1)
          cur_gap = 0
        else:
          first_fits = True
          break
      else:
        cur_gap += 1

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
      return
      
      
  def _mark_completed_clues_helper_new(self, line, clues, indices):
    cur_mark_length = 0
    line_length = len(line)
    remaining_total = self.get_clues_total(clues)
    if clues:
       cur_clue = clues.pop(0)
    else:
       cur_clue = 0;
    steps_taken = 0
    steps_taken_since_last_x =0
    for i in indices:
      print("---------------------------------")
      print("Current index:", i)
      print("Steps left:{}".format(line_length - steps_taken))
      print("Steps since last x:",steps_taken_since_last_x)
      print("Remaining total:{}".format(remaining_total))
      print("Current clue:{}".format(cur_clue))
      print("Current mark length:", cur_mark_length)
      print("Cell value:",line[i])
      
      made_mark = False
      if line[i] == 1:
        print("Index:{} is filled in".format(i))
        cur_mark_length += 1
        print("Current mark length:", cur_mark_length)
      else:
        not_too_much_room_before = steps_taken_since_last_x < (cur_clue + 2)
        print("not_too_much?: {}, Steps taken since last x:{}, cur_clue +1:{}".format(not_too_much_room_before,steps_taken_since_last_x, cur_clue+1))
        if cur_mark_length == cur_clue and not_too_much_room_before:
          print("Mark & clue equal, mark and go to next clue:", cur_mark_length)
          
          self._mark_range(line, i, 1, -1)
#          index_before_cur_mark = i - cur_mark_length
#          if (index_before_cur_mark > 0):
#            if line[i-cur_mark_length] == 0:
#              self._mark_range(line, i-cur_mark_length, 1, -1)
          steps_taken_since_last_x = 0
          made_mark = True;
#        elif cur_mark_length < cur_clue:
#          print("Reset steps taken since last x")
#          steps_taken_since_last_x = 0
#        elif line[i] == -1 and steps_taken_since_last_x >= cur_clue:
#          print("Space between current spot and last X is equal to clue, very likely fits")
#          self._mark_range(line, i-cur_clue, cur_clue, 1)
        cur_mark_length = 0
      steps_minus_clue = steps_taken - (cur_clue+1)
      line_minus_total = line_length - remaining_total
      should_go = (steps_minus_clue >= line_minus_total) or made_mark
      print("Should go to next clue? {} Steps taken - cur clue: {}, line length - remaining total: {}".format(should_go, steps_minus_clue, line_minus_total))
      if should_go:
        print("There isn't room left for the rest of the clues, or we made a mark, get next clue.")
        remaining_total = self.get_clues_total(clues)
        if clues:
          cur_clue = clues.pop(0)
        else:
          cur_clue = 0;
        steps_taken_since_last_x = 0
      steps_taken += 1
      steps_taken_since_last_x += 1

  def _mark_completed_clues(self, line, clues):
    print("****** Going forward through line")
    print("Clues:", clues)
    clues_copy = clues.copy()
    self._mark_completed_clues_helper_new(line, clues_copy, range(len(line)))
    print("****** Going backward through line")
    reversed_clues_copy = clues.copy()[::-1]
    self._mark_completed_clues_helper_new(line, reversed_clues_copy, reversed(range(len(line))))
        
  def test_solve(self):
    self.board[0,4] = 1
    self.board[1,0] = 1
    self.board[1,3] = 1
    self.board[1,4] = 1
    self.board[1,8] = 1
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
    self._mark_completed_clues(self.board[0,...], self.rows[0])
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
    self._mark_completed_clues(self.board[1,...], self.rows[1])
  
  def solve(self):      
    # First find empy, or full rows/columns
    # Rows
#    for idx,row in enumerate(self.rows):
#      line = self.board[idx,...]
#      if self.get_clues_total(row) == 0:
#        # Empty row, set all to X
#        self._set_range(True, idx, 0, self.width, "X")
#        self._mark_range(line, 0, self.width, -1)
#      elif self.get_clues_total(row) == self.width:
#        # Row is full, populate accordingly
#        cur_idx = 0
#        for clue in row:
#          #Fill in length of clue
#          self._set_range(True, idx, cur_idx, clue, "O")
#          self._mark_range(line, cur_idx, clue, 1)
#          cur_idx += clue
#          #Add spacer
#          if cur_idx < self.width:
#            self._set_range(True, idx, cur_idx, 1, "X")
#            self._mark_range(line, cur_idx, 1, -1)
#            cur_idx += 1
#
#    # Columns
#    for idx,col in enumerate(self.columns):
#      line = self.board[...,idx]
#      if self.get_clues_total(col) == 0:
#        # Empty column, set all to X
#        self._set_range(False, idx, 0, self.height, "X")
#        self._mark_range(line, 0, self.height, -1)
#      elif self.get_clues_total(col) == self.height:
#        # Column is full, populate accordingly
#        cur_idx = 0
#        for clue in col:
#          #Fill in length of clue
#          self._set_range(False, idx, cur_idx, clue, "O")
#          self._mark_range(line, cur_idx, clue, 1)
#          cur_idx += clue
#          # Add spacer
#          if cur_idx < self.width:
#            self._set_range(False, idx, cur_idx, 1, "X")
#            self._mark_range(line, cur_idx, 1, -1)
#            cur_idx += 1
    while True:
      for idx, row in enumerate(self.rows):
        self._fill_guaranteeds(self.board[idx,...], row)
#        self._fill_impossible(self.board[idx,...], row)
#        self._find_guaranteeds(True, idx, row)
#        self._find_impossible(True, idx, row)

      for idx, col in enumerate(self.columns):
        self._fill_guaranteeds(self.board[..., idx], col)
#        self._fill_impossible(self.board[...,idx], col)
#        self._find_guaranteeds(False, idx, col)
#        self._find_impossible(False, idx, col)
      
#      print("Mark completed clues for row:{}, clues:{}".format(self.board[7,...], self.rows[7]))
#      self._mark_completed_clues(self.board[7,...], self.rows[7])
      
      for idx in range(self.height):
        print("Mark completed clues for row:{}, clues:{}".format(self.board[idx,...], self.rows[idx]))
        self._mark_completed_clues(self.board[idx,...], self.rows[idx])

      for idx in range(self.width):
        print("Mark completed clues for column:{}, clues:{}".format(self.board[...,idx], self.columns[idx]))
        self._mark_completed_clues(self.board[...,idx], self.columns[idx])


      break
    # Fill guaranteed cells (numbers in a line with a total close enough to the size of the line)
    # Fill other known cells, ones close enough to a boundary (edge or X) that must have others filled based on numbers
    # Find "impossible" cells, ones that cannot be filled due to presence of other fills or Xs

#print("Hello world")
#b = NonogramBoard([[5],[0],[1,1,1],[3,1],[4]],[[1,2],[1,2],[1,3],[1,1],[1,3]])
#b.solve()
#print("Board:")
#print("{}".format(str(b)))

#completed_board = np.array([[1.,1,-1,-1,1,1,1,1,1,-1],
#         [-1,-1,1,-1,-1,-1,-1,-1,-1,-1],
#         [1,-1,1,1,-1,-1,-1,-1,1,-1],
#         [1,-1,-1,-1,-1,1,-1,1,1,1],
#         [-1,1,-1,-1,1,1,-1,1,-1,1],
#         [-1,-1,-1,-1,1,1,1,1,-1,1],
#         [1,-1,-1,1,1,-1,1,1,1,-1],
#         [1,-1,-1,1,1,-1,1,-1,1,-1],
#         [1,-1,1,1,-1,-1,1,-1,1,1],
#         [-1,1,1,-1,-1,-1,1,-1,-1,1]])
#
#print(print_array(completed_board))
# Valid 10x10
c = NonogramBoard([[2,5], [1], [1,2,1], [1,1,3], [1,2,1,1], [4,1], [1,2,3], [1,3,1,1], [1,2,1,2], [2,1,1]],
                  [[1,2,3], [1,1,1], [2,3], [1,3], [1,4], [1,3], [1,5], [1,4], [1,2,3], [3,2]])
c.solve()

print("C Board:")
print("{}".format(str(c)))
 
#test 2x10
#d = NonogramBoard([[1,4], [1,3,1,1]],[[2],[0],[2],[2],[2],[1],[1],[0],[1],[0]])
#
#d.test_solve()
#print("D Board:")
#print("{}".format(str(d)))

# Valid 15x15

e = NonogramBoard([[6,2,1,2],[1,6,1],[1,1,2,1,1],[2,1,8],[2,1,5,1],[3,4,5],[2,1,3,4],[1,2,3,2],[5,4,1],[4,2,4,2],[3,2,2,5],[1,1,1,2,3],[1,1,1,5],[4,2,4],[1,3,1,3,1]],
                  [[7,2],[1,2,3,2],[4,1,3,2],[1,2,1,2,3],[2,2,2,2,1],[4,1,1,2],[2,3,1],[3,2,1,4],[5,1,3,2],[2,2,3,2],[4,6,1],[1,5,2,3],[1,4,5],[1,2,3,5],[1,9,2]])
e.solve()
print("E Board:")
print("{}".format(str(e)))
