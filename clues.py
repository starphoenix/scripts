import numpy as np
from bisect import bisect

print_debug_messages = False

def d_print(*output):
  if print_debug_messages: print(*output)
  
def array_to_string(array):
  mapping = {
    "float": lambda x: "_" if (x == 0) else ("■" if (x == 1) else "X")
  }
  return np.array2string(array, None, None, None, "|", "", formatter=mapping)

#Clue#######################
class Clue:
  def __init__(self, value, name, line_length):
    self.value = value
    self.name = name
    self.line_length = line_length
    self.possible_positions = list(range(0, line_length))
    self.definite_positions = []
    self.solved = False
    if value == 0:
      self.possible_positions = []
      self.solved = True
    elif value == line_length:
      self.definite_positions = self.possible_positions.copy()
      self.solved = True
    elif value >= line_length/2:
      length_of_unknowns = line_length - value
      self.definite_positions = self.possible_positions[length_of_unknowns:-length_of_unknowns].copy()
      
    
  def __repr__(self):
    return "({}: {})".format(self.name, self.value)
    
  def insert_definite(self, index):
    insertion_idx = bisect(self.definite_positions, index)
    self.definite_positions.insert(insertion_idx, index)
  
  def set_definite(self, index):
    d_print("Adding index {} to definites for clue:{}".format(index, self))
    if index not in self.possible_positions:
      d_print("For clue:{}, definite index {} not in possibles, we got something wrong".format(self, index))
    else:
      if index in self.definite_positions:
        d_print("Already marked this definite, nothing to do here.")
        return
      else:
        self.insert_definite(index)
        d_print("Added {} to definites for clue:{} definites: {}".format(index, self, self.definite_positions))
        min_definite = min(self.definite_positions)
        max_definite = max(self.definite_positions)
        for idx in range(min_definite, max_definite):
          if idx not in self.definite_positions:
            d_print("Filling in necessary definite index: {} for clue: {}".format(idx, self))
            self.insert_definite(idx)
        d_print("Definites after adding:",self.definite_positions)
        self.possible_positions[:] = [position for position in self.possible_positions if (position > max_definite - self.value) and (position < min_definite + self.value)]
        d_print("Possibles after pruning:",self.possible_positions)
        if len(self.definite_positions) == self.value:
          d_print("Solved!")
          self.solved = True
        
  def remove_possibility(self, index):
    d_print("Removing index {} from possiblities for clue:{}".format(index, self))
    if index not in self.possible_positions:
      d_print("Can't remove possibility from clue {} because it is not in the list of possibilities".format(self))
      d_print("Clue:{}, possibles:".format(self, self.possible_positions))
      if len(self.possible_positions) == self.value and self.areElementsContiguous(self.possible_positions):
        d_print("Length of remaining possibles and value are the same, and remaining possibles are contiguous: all possibles must be definites.")
        d_print("Remaining possibles:{}, value: {}".format(self.possible_positions, self.value))
        for idx in self.possible_positions:
          if idx not in self.definite_positions:
            self.set_definite(idx)
    elif index in self.definite_positions:
      d_print("Can't remove possibility from clue {} because it is already marked definite".format(self))
    else:
      min_possible = min(self.possible_positions)
      max_possible = max(self.possible_positions)
      possibles_higher_than_index = [position for position in self.possible_positions if (position > index)]
      d_print("Possibles higher than index: {}",possibles_higher_than_index)
      #if count of numbers higher than index is less than value, remove those numbers.
      if len(possibles_higher_than_index) < self.value:
        d_print("removing possibles higher than {}: {}".format(index, possibles_higher_than_index))
        self.possible_positions[:] = [position for position in self.possible_positions if (position <= index)]
        d_print("removed possibles higher than {}, left with {}".format(index, self.possible_positions))
      possibles_lower_than_index = [position for position in self.possible_positions if (position < index)]
      d_print("Possibles lower than index: {}",possibles_lower_than_index)
      #if count of numbers lower than index is less than value, remove those numbers.
      if len(possibles_lower_than_index) < self.value:
        d_print("removing possibles lower than {}: {}".format(index, possibles_lower_than_index))
        self.possible_positions[:] = [position for position in self.possible_positions if (position >= index)]
        d_print("removing possibles lower than {}, left with {}".format(index, self.possible_positions))
      self.possible_positions.remove(index)
      d_print("Removed possible position {}, left with {}".format(index, self.possible_positions))
      if len(possibles_higher_than_index) != len(possibles_lower_than_index):
#        if not self.possible_positions:
#          print("Clue: {}", self)
#          print(self.possible_positions)
#          print(self.definite_positions)
        min_possible = min(self.possible_positions)
        max_possible = max(self.possible_positions)
        last_guaranteed = min_possible + self.value-1
        first_guaranteed = max_possible - self.value+1
        d_print("min possible:{} max possible:{} last guaranteed:{} first_guaranteed: {}".format(min_possible, max_possible, last_guaranteed, first_guaranteed))
        if len(self.possible_positions) == self.value and self.areElementsContiguous(self.possible_positions):
          d_print("Length of remaining possibles and value are the same, and remaining possibles are contiguous: all possibles must be definites.")
          d_print("Remaining possibles:{}, value: {}".format(self.possible_positions, self.value))
          for idx in self.possible_positions:
            if idx not in self.definite_positions:
              self.set_definite(idx)
        elif first_guaranteed <= last_guaranteed:
          d_print("Determined that indices {} are definites. Adding now...".format(range(first_guaranteed, last_guaranteed+1)))
          for idx in range(first_guaranteed, last_guaranteed+1):
            if idx not in self.definite_positions:
              self.set_definite(idx)
        
      d_print("Removed index {} for clue {}. Left with: Possibles: {}, Definites: {}".format(index,self, self.possible_positions, self.definite_positions))
  
  def areElementsContiguous(self, arr):
    # After sorting, check if
    # current element is either
    # same as previous or is
    # one more.
    for i in range(1,len(arr)):
        if (arr[i] - arr[i-1] > 1) :
            return 0
    return 1

#Clue Line########################
class ClueLine:
  def __init__(self, clues, line):
    self.clues = clues
    self.line = line
    self.length = len(line)
    if not clues:
      self.solved = True
      line[...] = -1
    else:
      self.solved = False
      self.remove_possibilities()
      self.update_state()
    
  # Returns the sum of the clues in a given line plus the spacers between them.
  def get_clues_total(self, clues):
    total = 1
    for clue in clues:
      total += clue.value
    total += len(clues) - 1
    return total if total > 0 else 0
    
  def get_clue_matching_cell(self, index):
    clue_matching_cell = None
    for clue in self.clues:
      if index in clue.possible_positions:
        if clue_matching_cell:
          clue_matching_cell = None
          break
        clue_matching_cell = clue
    return clue_matching_cell
  
  def get_possible_clues_for_cell(self, index):
    possible_clues = []
    for clue in self.clues:
      if index in clue.possible_positions:
        possible_clues.append(clue)
    return possible_clues
    
  def update_state(self):
    steps = 0
    while True: #do
      prev_line = self.line.copy()
      d_print("Previous line:", array_to_string(prev_line))
      self.update_cells_from_clues()
      self.update_clues_from_cells()
      self.check_for_solved_clues()
      self.check_for_contiguous_eliminations()
      self.check_for_impossible_cells()
      self.check_for_solved_clues()
      # if steps are greater than length, i think something is probably wrong.
      d_print("Previous line: {} current line: {}".format(array_to_string(prev_line), array_to_string(self.line)))
      if np.array_equal(prev_line, self.line) or steps > self.length:
        break
      steps += 1
      for clue in self.clues:
        d_print("Clue: {}, definites: {}, possibles: {}".format(clue, clue.definite_positions, clue.possible_positions))
    if not 0 in self.line:
      self.solved = True
    
  def update_cells_from_clues(self):
    d_print("Updating cells from possible clue changes!")
    # The concept here is that some changes have may have been made within our clues to their definites.
    # in other words, the clues may know that some cells belong to them, but the line might not be reflecting that.
    # Similarly, once a cell has been removed from all its clues' possibilities, we can mark it X.
    # I expect this might also involve updating other clues.
    
    it = np.nditer(self.line, flags=['f_index'], op_flags=['readwrite'])
    for cell_value in it:
      for clue in self.clues:
#        if not clue.solved:
        if it.index in clue.definite_positions:
          #For some reason with numpy array iterators you have to do cell_val[...] to modify the value
          #cell_val = value will only modify cell_val within local scope
          cell_value[...] = 1
      
  
  def update_clues_from_cells(self):
    d_print("Updating clues from possible cell changes!")
    it = np.nditer(self.line, flags=['f_index'], op_flags=['readwrite'])
    for cell_val in it:
      if cell_val == 1: #it.index is filled
        #If the cell is in only one clue's possibilities, then we can tell that cell to set definite.
        #If the cell is in more than one clue's possibilities, then we cannot do anything about it at the moment.
        clue_matching_cell = self.get_clue_matching_cell(it.index)
        if clue_matching_cell:
          clue_matching_cell.set_definite(it.index)
      elif cell_val == -1: #it.index is crossed out
        #Cell has to be removed from all clue's possiblities
        for clue in self.clues:
          #In theory it's okay to just call this even if it's not in the clue's possibilities because we check that inside the func.
#          print(array_to_string(self.line))
          clue.remove_possibility(it.index)
      #else is a no-op i think?
  
  def check_for_solved_clues(self):
    d_print("Checking for solved clues!")
    for clue in self.clues:
      if clue.solved and clue.value > 0:
        d_print("Clue {} is solved. Definite positions: {}".format(clue, clue.definite_positions))
        index_prior_to_definites = min(clue.definite_positions) - 1
        index_after_definites = max(clue.definite_positions) + 1
        d_print("Index prior to definites:", index_prior_to_definites)
        d_print("Index after definities:", index_after_definites)
        if index_prior_to_definites >= 0:
          self.line[index_prior_to_definites] = -1
        if index_after_definites < self.length:
          self.line[index_after_definites] = -1
        for idx in clue.definite_positions:
          d_print("Setting index: {} to filled".format(idx))
          self.line[idx] = 1
      elif clue.solved and clue.value == 0:
        self.line[...] = -1
          
  def check_for_impossible_cells(self):
    d_print("Checking for impossible cells!")
    it = np.nditer(self.line, flags=['f_index'], op_flags=['readwrite'])
    for cell_value in it:
      in_any_clues_possibles = False
      for clue in self.clues:
        if it.index in clue.possible_positions:
          in_any_clues_possibles = True
      if not in_any_clues_possibles:
        d_print("Index:{} not in any clues' possibles".format(it.index))
        cell_value[...] = -1
  
  def check_for_contiguous_eliminations(self):
    d_print("Checking for contiguous eliminations!")
    it = np.nditer(self.line, flags=['f_index'], op_flags=['readwrite'])
    contiguous_cell_length = 0
    for cell_value in it:
      if cell_value == 1:
        contiguous_cell_length += 1
        d_print("Filled cell at index:{}, contiguous cell length:{}".format(it.index, contiguous_cell_length))
      else:
        d_print("Non-filled cell at index:{} resetting contiguous cell length".format(it.index))
        contiguous_cell_length = 0
      possible_clues = self.get_possible_clues_for_cell(it.index)
      d_print("Possible clues for index: ", it.index, possible_clues)
      if possible_clues:
        for clue in possible_clues:
          if contiguous_cell_length > clue.value:
            d_print("Index {} does not belong to clue {}".format(it.index, clue))
            #This index does NOT belong to clue, therefore the next index also does not belong to clue
            stop_index = it.index + 1
            if stop_index >= self.length: stop_index = self.length - 1
            for index in range(it.index - contiguous_cell_length, stop_index+1):
              clue.remove_possibility(index)
    
  def remove_possibilities(self):
    d_print("Removing possibilities!")
    for idx, cur_clue in enumerate(self.clues):
      d_print("_")
      d_print("Removing possibilities from clue: ", cur_clue)
      #Find clues preceding this clue
      prior_clues = self.clues[:idx]
      d_print("Prior clues:", prior_clues)
      #Find clues following this clue
      following_clues = []
      if idx+1 < len(self.clues):
        following_clues = self.clues[idx+1:]
      d_print("Following clues:", following_clues)
      #find last index in line that must belong to all clues prior to this one (that's the first index for this clue)
      first_index = self.get_clues_total(prior_clues)
      #find the first index in line that must belong to all clues after this one
      last_index = self.length - self.get_clues_total(following_clues)
#      if prior_clues and following_clues:
      last_index -= 1
      #remove from possibilities in the clue only those indices that are not in any of the above two sets.
      d_print("For clue:{}({}) first possible index: {}, last possible index: {}".format(cur_clue, idx, first_index, last_index))
      if last_index - first_index + 1 == cur_clue.value:
        d_print("Distance between first and last index equal to clue, this should mean we can set the clue's definite positions now.")
        for idx_to_set in range(first_index, last_index +1):
          cur_clue.set_definite(idx_to_set)
      else:
        for idx_to_remove in range(0, self.length):
          if idx_to_remove not in range(first_index, last_index+1):
            if not cur_clue.solved:
              cur_clue.remove_possibility(idx_to_remove)
      d_print("For clue:{}({}) definite positions:{} possible positions: {}".format(cur_clue, idx, cur_clue.definite_positions, cur_clue.possible_positions))
      
  def set_cell(self, index, value):
    #ideally value is always -1 or 1, as any other value is nonsense to our board
    d_print("Setting cell:{} to value:{}".format(index, value))
    if self.line[index] not in {-1, 1}:
      self.line[index] = value
    self.update_state()
    
  
  def fill_in_cell(self, index_to_fill):
    d_print("Filling in cell:", index_to_fill)
#  def fill_in_definites(self):
#    for idx, cur_clue in enumerate(self.clues):
#      first_possible_index = cur_clue.possible_positions[0]
#      last_possible_index = cur_clue.possible_positions[-1]
#      dist = last_possible_index - first_possible_index + 1
#      length_of_definites = dist - cur_clue.value
#      if length_of_definites < 0:
#        length_of_definites = 0
#      if length_of_definites > cur_clue.value:
#        d_print("For clue:{} length of definites longer than clue, therefore no definites".format(cur_clue))
#      d_print("For clue:{} First possible position: {} Last possible position: {}, dist: {}, length of definites:{}".format(cur_clue, first_possible_index, last_possible_index, dist, length_of_definites))
#      cur_clue.definite_positions = cur_clue.possible_positions[length_of_definites:-length_of_definites]
#      d_print("For clue:{} definite positions: {}".format(cur_clue, cur_clue.definite_positions))
      
  
  def print_state(self):
    clues_for_index = ['']*self.length
    for idx, cell in enumerate(clues_for_index):
      for clue in self.clues:
        if idx in clue.possible_positions:
          clues_for_index[idx] += clue.name + " "
      clues_for_index[idx] = clues_for_index[idx][:-1]
    output = "["
    for idx, elements in enumerate(clues_for_index):
      if elements:
        output += "{}|".format(elements)
      else:
        output += "X|"
    output = output[:-1]
    output += "]"
    definites_output = array_to_string(self.line)
    if self.solved:
      definites_output += "✓"
    print("P: ", output)
    print("D: ", definites_output)
    
    
  def idk(self):
    self.clues[0].remove_possibility(4)
#############
#print_debug_messages = True
#
#line_length = 10
#line = np.zeros([line_length])
#c = ClueLine([Clue(4, 'a',line_length),Clue(1, 'b',line_length)], line)

#c = ClueLine([Clue(1, "a", line_length), Clue(1,"b", line_length), Clue(1,"c", line_length)], line)
#
#print(range(2,3))
#c.print_state()
#input()
#c.set_cell(6, 1)
#c.print_state()
#input()
#c.set_cell(7, 1)
#c.print_state()
#c.set_cell(8,1)
#c.print_state()

def get_clues_total(clueset):
  total = 1
  for clue in clueset:
    total += clue
  total += len(clueset) - 1
  return total if total > 0 else 0

def get_possible_cluesets_helper(cur_cluesets, clueset, clue_value, length):
  possible_clueset = clueset + [clue_value]
  clueset_length = get_clues_total(possible_clueset)
  d_print("Possible clueset:", possible_clueset)
  d_print("Clueset length: ", clueset_length)
  if clueset_length > length+1:
    #This clueset cannot fit in this length
    d_print("This clueset cannot fit in this length. Returning cur_cluesets:", cur_cluesets)
    return cur_cluesets
  else:
    cur_cluesets += [possible_clueset]
    next_cluesets = get_possible_cluesets_helper(cur_cluesets, possible_clueset, clue_value, length)
    if next_cluesets == cur_cluesets:
      d_print("A new clue of {} could not fit. cur_cluesets:{}".format(clue_value, cur_cluesets))
      d_print("clueset:{}, possible clueset:{}".format(clueset, possible_clueset))
      #a new clue of clue_value could not fit.
      #increase the value of the last element of possible clueset and call again with a cluevalue of 1
      return get_possible_cluesets_helper(cur_cluesets, possible_clueset[0:-1], possible_clueset[-1]+1, length)
    #we were succesfully able to fit another clue of clue_value on to the end
    #next we want to try to fit another clue of 1 on the end.
    d_print("We were able to fit another clue of {} on the end.".format(clue_value))
    d_print("Now try to add another clue of value 1.")
    return get_possible_cluesets_helper(next_cluesets, possible_clueset, 1, length)

def get_possible_cluesets(length):
  return get_possible_cluesets_helper([], [], 1, length)
  
#length = 20
#s = [[0]] #Add in the empty set
#s.extend(get_possible_cluesets(length))
#print(s)
#
#for clueset in s:
#  clues = []
#  name = 'a'
#  for val in clueset:
#    clues.append(Clue(val, name, length))
#    name = chr(ord(name) + 1)
#  print(clues)
#  line = np.zeros([length])
#  clue_line = ClueLine(clues, line)
#  clue_line.remove_possibilities()
#  clue_line.update_state()
#  clue_line.print_state()

#ClueBoard
# Will have a board represented by a numpy 2D array
# Will have a ClueLine for every single row and column of clues
# Each ClueLine has a reference to its line in the numpy 2D array
# After each ClueLine operation:
#   check for differences between prev state and new state
#   for each difference, update the corresponding row and column ClueLine.

class ClueBoard:
  def __init__(self, row_cluesets, col_cluesets):
    #length of rows = num of columns
    #length of columns = num of rows
    row_length = len(col_cluesets)
    col_length = len(row_cluesets)
    self.board = np.zeros([col_length, row_length])
    self.solved = False
    name = 'A'
    index = 0
    self.row_lines = []
    for row_clueset in row_cluesets:
      clues_for_row = []
      for row_clue in row_clueset:
        clues_for_row.append(Clue(row_clue, name, row_length))
        name = chr(ord(name) + 1)
      line = ClueLine(clues_for_row, self.board[index,...])
      self.row_lines.append(line)
      index += 1
    
    index = 0
    self.col_lines = []
    for col_clueset in col_cluesets:
      clues_for_col = []
      for col_clue in col_clueset:
        clues_for_col.append(Clue(col_clue, name, col_length))
        name = chr(ord(name) + 1)
      self.col_lines.append(ClueLine(clues_for_col, self.board[...,index]))
      index += 1
      
  def print_state(self):
    print(array_to_string(self.board))
    
  def solve(self, tolerance):
    steps = 0
    while True: #do
      d_print("Solve step ", steps)
      prev_board = self.board.copy()
      line_idx = 0
      for line in self.row_lines:
        d_print("Updating row index: ", line_idx)
        d_print("Clues:", line.clues)
        line.update_state()
#        self.print_state()
#        input()
        line_idx+=1
      line_idx = 0
      for line in self.col_lines:
        d_print("Updating col index: ", line_idx)
        d_print("Clues:", line.clues)
        line.update_state()
#        self.print_state()
#        input()
        line_idx +=1
      if np.array_equal(prev_board, self.board) or steps > tolerance:
        d_print("Breaking from solve")
        if steps > tolerance:
          d_print("Broke due to surpassing tolerance")
        break;
      steps += 1
      if 0 not in self.board:
        self.solved = True
        break;
    

#Sample 5x5
#board = ClueBoard([[5],[0],[1,1,1],[3,1],[4]],[[1,2],[1,2],[1,3],[1,1],[1,3]])

#Sample 10x10
#board = ClueBoard([[2,5], [1], [1,2,1], [1,1,3], [1,2,1,1], [4,1], [1,2,3], [1,3,1,1], [1,2,1,2], [2,1,1]],
#                  [[1,2,3], [1,1,1], [2,3], [1,3], [1,4], [1,3], [1,5], [1,4], [1,2,3], [3,2]])

#Sample 15x15
#board = ClueBoard([[6,2,1,2],[1,6,1],[1,1,2,1,1],[2,1,8],[2,1,5,1],[3,4,5],[2,1,3,4],[1,2,3,2],[5,4,1],[4,2,4,2],[3,2,2,5],[1,1,1,2,3],[1,1,1,5],[4,2,4],[1,3,1,3,1]],
#                  [[7,2],[1,2,3,2],[4,1,3,2],[1,2,1,2,3],[2,2,2,2,1],[4,1,1,2],[2,3,1],[3,2,1,4],[5,1,3,2],[2,2,3,2],[4,6,1],[1,5,2,3],[1,4,5],[1,2,3,5],[1,9,2]])

#Sample 20x20
board = ClueBoard([[1,2,6],[9,1],[1,11,3],[7,7,1],[9,10],[12,2],[6],[2,3],[10],[10],[11,2],[1,13,4],[2,5,2,1,3],[1,1,2,1,2],[4,3],[4,1,2],[1,3,1,3],[2,2,3,1,1],[3,2,7],[4,3,6]],
                  [[1,4,3,2,2],[1,3,1,2,2],[5,1,3,3],[6,1,4,1],[6,2,1,1],[7,3,2],[7,3,1,3],[2,3,3,1,2],[2,3,5,1],[3,1,3,1],[4,5],[4,5],[1,3,4],[1,2,4,2],[1,2,5,5],[1,2,4,1,6],[1,1,2,1,2,1,2],[1,1,2,3,2,1,3],[1,2,2,4,2],[4,2,4,3]])
#
#print_debug_messages = True
if board:
  board.print_state()
  if board.solved == False:
    board.solve(15)
    board.print_state()



#s = input()
#input_clues = list(map(int, s.split(',')))
#length = int(input())
#print(type(length))
#name = 'a'
#clues = []
#for val in input_clues:
#  clues.append(Clue(val, name, length))
#  name = chr(ord(name) + 1)
#print(clues)
#line = np.zeros([length])
#print(line)
#clue_line = ClueLine(clues, line)
#clue_line.remove_possibilities()
#clue_line.update_state()
#clue_line.print_state()
