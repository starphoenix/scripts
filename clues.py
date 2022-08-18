import numpy as np
from bisect import bisect

#Clue#######################
class Clue:
  def __init__(self, value, name, line_length):
    self.value = value
    self.name = name
    self.line_length = line_length
    self.possible_positions = list(range(0, line_length))
    self.definite_positions = []
    self.solved = False
    if value == line_length:
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
  
  def set_definite(self, index, debug):
    if debug: print("Adding index {} to definites for clue:{}".format(index, self))
    if index not in self.possible_positions:
      if debug: print("For clue:{}, definite index {} not in possibles, we got something wrong".format(self, index))
    else:
      if index in self.definite_positions:
        if debug: print("Already marked this definite, nothing to do here.")
        return
      else:
        self.insert_definite(index)
        if debug: print("Added {} to definites for clue:{} definites: {}".format(index, self, self.definite_positions))
        min_definite = min(self.definite_positions)
        max_definite = max(self.definite_positions)
        for idx in range(min_definite, max_definite):
          if idx not in self.definite_positions:
            if debug: print("Filling in necessary definite index: {} for clue: {}".format(idx, self))
            self.insert_definite(idx)
        if debug: print("Definites after adding:",self.definite_positions)
        self.possible_positions[:] = [position for position in self.possible_positions if (position > max_definite - self.value) and (position < min_definite + self.value)]
        if debug: print("Possibles after pruning:",self.possible_positions)
        if len(self.definite_positions) == self.value:
          if debug: print("Solved!")
          self.solved = True
        
  def remove_possibility(self, index, debug):
    if debug: print("Removing index {} from possiblities for clue:{}".format(index, self))
    if index not in self.possible_positions:
      if debug: print("Can't remove possibility from clue {} because it is not in the list of possibilities".format(self))
    elif index in self.definite_positions:
      if debug: print("Can't remove possibility from clue {} because it is already marked definite".format(self))
    else:
      min_possible = min(self.possible_positions)
      max_possible = max(self.possible_positions)
      possibles_higher_than_index = [position for position in self.possible_positions if (position > index)]
      if debug: print("Possibles higher than index: {}",possibles_higher_than_index)
      #if count of numbers higher than index is less than value, remove those numbers.
      if len(possibles_higher_than_index) < self.value:
        if debug: print("removing possibles higher than {}: {}".format(index, possibles_higher_than_index))
        self.possible_positions[:] = [position for position in self.possible_positions if (position <= index)]
        if debug: print("removed possibles higher than {}, left with {}".format(index, self.possible_positions))
      possibles_lower_than_index = [position for position in self.possible_positions if (position < index)]
      if debug: print("Possibles lower than index: {}",possibles_lower_than_index)
      #if count of numbers lower than index is less than value, remove those numbers.
      if len(possibles_lower_than_index) < self.value:
        if debug: print("removing possibles lower than {}: {}".format(index, possibles_lower_than_index))
        self.possible_positions[:] = [position for position in self.possible_positions if (position >= index)]
        if debug: print("removing possibles lower than {}, left with {}".format(index, self.possible_positions))
      self.possible_positions.remove(index)
      if debug: print("Removed possible position {}, left with {}".format(index, self.possible_positions))
      if len(possibles_higher_than_index) != len(possibles_lower_than_index):
        min_possible = min(self.possible_positions)
        max_possible = max(self.possible_positions)
        last_guaranteed = min_possible + self.value-1
        first_guaranteed = max_possible - self.value+1
        if debug: print("min possible:{} max possible:{} last guaranteed:{} first_guaranteed: {}".format(min_possible, max_possible, last_guaranteed, first_guaranteed))
        if debug: print("Determined that indices {} are definites. Adding now...".format(range(first_guaranteed, last_guaranteed+1)))
        for idx in range(first_guaranteed, last_guaranteed+1):
          if idx not in self.definite_positions:
            self.set_definite(idx, debug)
      if debug: print("Removed index {} for clue {}. Left with: Possibles: {}, Definites: {}".format(index,self, self.possible_positions, self.definite_positions))

#Clue Line########################
class ClueLine:
  def __init__(self, clues, length):
    self.clues = clues
    self.length = length
    
  # Returns the sum of the clues in a given line plus the spacers between them.
  def get_clues_total(self, clues):
    total = 1
    for clue in clues:
      total += clue.value
    total += len(clues) - 1
    return total if total > 0 else 0
    
  def remove_possibilities(self, debug):
    for idx, cur_clue in enumerate(self.clues):
      #Find clues preceding this clue
      prior_clues = self.clues[:idx]
      if debug: print("Prior clues:", prior_clues)
      #Find clues following this clue
      following_clues = []
      if idx+1 < len(self.clues):
        following_clues = self.clues[idx+1:]
      if debug: print("Following clues:", following_clues)
      #find last index in line that must belong to all clues prior to this one (that's the first index for this clue)
      first_index = self.get_clues_total(prior_clues)
      #find the first index in line that must belong to all clues after this one
      last_index = self.length - self.get_clues_total(following_clues)
      #remove from possibilities in the clue only those indices that are not in any of the above two sets.
      if debug: print("For clue:{}({}) first possible index: {}, last possible index: {}".format(cur_clue, idx, first_index, last_index))
      for idx_to_remove in range(0, self.length):
        if idx_to_remove not in range(first_index, last_index):
          if not cur_clue.solved:
            cur_clue.remove_possibility(idx_to_remove, debug)
      if debug: print("For clue:{}({}) possible positions: {}".format(cur_clue, idx, cur_clue.possible_positions))
      
  def fill_in_definites(self, debug):
    for idx, cur_clue in enumerate(self.clues):
      first_possible_index = cur_clue.possible_positions[0]
      last_possible_index = cur_clue.possible_positions[-1]
      dist = last_possible_index - first_possible_index + 1
      length_of_definites = dist - cur_clue.value
      if length_of_definites < 0:
        length_of_definites = 0
      if length_of_definites > cur_clue.value:
        if debug: print("For clue:{} length of definites longer than clue, therefore no definites".format(cur_clue))
      if debug: print("For clue:{} First possible position: {} Last possible position: {}, dist: {}, length of definites:{}".format(cur_clue, first_possible_index, last_possible_index, dist, length_of_definites))
      cur_clue.definite_positions = cur_clue.possible_positions[length_of_definites:-length_of_definites]
      if debug: print("For clue:{} definite positions: {}".format(cur_clue, cur_clue.definite_positions))
      
  
  def print_state(self, definites_or_possibles):
    print("{}:".format(self.clues))
    line = ['']*self.length
    for idx, cell in enumerate(line):
      for clue in self.clues:
        if definites_or_possibles:
          if idx in clue.definite_positions:
            line[idx] = clue.name
        else:
          if idx in clue.possible_positions:
            line[idx] += clue.name + " "
    output = "["
    for idx, elements in enumerate(line):
      if elements:
        output += "{}|".format(elements)
      else:
        output += " |" if definites_or_possibles else "X|"
    output = output[:-1]
    output += "]"
    line_solved = True
    for clue in self.clues:
      if not clue.solved:
        line_solved = False
      if not line_solved:
        break
    if line_solved:
      output += "✓"
    print(output)
    
  def idk(self):
    self.clues[0].remove_possibility(4, False)
#############


c = ClueLine([Clue(2, "a", 5), Clue(2,"b", 5)], 5)

print_debug_messages = True
#c.remove_possibilities(print_debug_messages)

#c.fill_in_definites(print_debug_messages)

#c.idk()

#c.print_state(True)
#c.print_state(False)

def get_clues_total(clueset):
  total = 1
  for clue in clueset:
    total += clue
  total += len(clueset) - 1
  return total if total > 0 else 0

def get_possible_cluesets_helper(cur_cluesets, clueset, clue_value, length, debug):
  possible_clueset = clueset + [clue_value]
  clueset_length = get_clues_total(possible_clueset)
  if debug:
    print("Possible clueset:", possible_clueset)
    print("Clueset length: ", clueset_length)
  if clueset_length > length+1:
    #This clueset cannot fit in this length
    if debug: print("This clueset cannot fit in this length. Returning cur_cluesets:", cur_cluesets)
    return cur_cluesets
  else:
    cur_cluesets += [possible_clueset]
    next_cluesets = get_possible_cluesets_helper(cur_cluesets, possible_clueset, clue_value, length, debug)
    if next_cluesets == cur_cluesets:
      if debug:
        print("A new clue of {} could not fit. cur_cluesets:{}".format(clue_value, cur_cluesets))
        print("clueset:{}, possible clueset:{}".format(clueset, possible_clueset))
      #a new clue of clue_value could not fit.
      #increase the value of the last element of possible clueset and call again with a cluevalue of 1
      return get_possible_cluesets_helper(cur_cluesets, possible_clueset[0:-1], possible_clueset[-1]+1, length, debug)
    #we were succesfully able to fit another clue of clue_value on to the end
    #next we want to try to fit another clue of 1 on the end.
    if debug:
      print("We were able to fit another clue of {} on the end.".format(clue_value))
      print("Now try to add another clue of value 1.")
    return get_possible_cluesets_helper(next_cluesets, possible_clueset, 1, length, debug)

def get_possible_cluesets(length, debug):
  return get_possible_cluesets_helper([], [], 1, length, debug)
  
length = 15
s = get_possible_cluesets(length, False)
#print(s)

for clueset in s:
  clues = []
  for val in clueset:
    clues.append(Clue(val, "{}".format(val), length))
  clue_line = ClueLine(clues, length)
  clue_line.remove_possibilities(False)
  clue_line.print_state(True)
