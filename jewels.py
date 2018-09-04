# implement the matching game Jewels in a machine-playable way, test
# various strategies

import random

#global game parameters. The rockbox jewels game has width=height=8, numberOfColours=7, vanishLength=3
width = 8
height = 8
numberOfColours = 7 # block colours will be represented by the numbers
# 1,2,...,numberOfColours, with 0 being an empty square
vanishLength = 3 # a collection of at least vanishLength blocks of the same
#colour in a vertical or horizontal line is called a mono.

class board:
    score = 0
    entries = [[0 for i in range(width)] for j in range(height)]

    def printEntries(self): #only for <10 colours
        for j in range(height):
            print " ".join(map(str, self.entries[j]))

    def randomize(self):
        for i in range(width):
            for j in range(height):
                self.entries[j][i] = random.randint(1, numberOfColours)

    def findMonos(self):
        # return a list whose elements correspond to the maximal monos
        # in the current board. Each element is a list of coordinates
        # making up the corresponding mono
        # if we stored the board as a numpy matrix we could extract the
        # rows or columns as vectors and so avoid writing all this stuff
        # twice...
        output = []
        #first, the horizontal monos
        for i in range(height):
            row = self.entries[i]
            currentColour = row[0]
            currentStreakStart = 0
            for j in range(1, width):
                if row[j] != currentColour:
                    if j - currentStreakStart >= vanishLength:
                        output.append([[i, x] for x in range(currentStreakStart, j)])
                    currentColour = row[j]
                    currentStreakStart = j
            # we hit the last entry, j=width. Was it the last entry of a
            # mono? if so, append it.
            if width - currentStreakStart >= vanishLength:
                output.append([[i, x] for x in range(currentStreakStart, width)])
        #now the vertical monos
        for j in range(width):
            currentColour = self.entries[0][j]
            currentStreakStart = 0
            for i in range(1, height):
                if self.entries[i][j] != currentColour:
                    if i - currentStreakStart >= vanishLength:
                        output.append([[x, j] for x in range(currentStreakStart, i)])
                    currentColour = self.entries[i][j]
                    currentStreakStart = i
            #we hit the last entry of the column, was it the last entry
            # of a mono? if so, append it to output
            if height - currentStreakStart >= vanishLength:
                output.append([[x, j] for x in range(currentStreakStart, height)])

        return output

    def gravity(self):
        for j in range(width):
            col = [self.entries[i][j] for i in range(height) if self.entries[i][j] != 0]
            newcol = [0 for x in range(height - len(col))] + col
            #make the first col equal to newcol
            for i in range(height):
                self.entries[i][j] = newcol[i]

    def randomFillZeroes(self):
        for i in range(height):
            for j in range(width):
                if self.entries[i][j] == 0:
                    self.entries[i][j] = random.randint(1, numberOfColours)

    def evolve(self):
        #repeat:
        # zero out any monos
        # update the score
        # gravity
        # random fill any spaces
        #until there are no more monos
        while len(self.findMonos()) != 0:
            monos = self.findMonos()
            for m in monos:
                self.score += len(m) - vanishLength + 1
                for x in m:
                    self.entries[x[0]][x[1]] = 0
            #debugging:
            #self.printEntries()
            #print "\nscore is now ", self.score, "\n"
            #end debugging
            self.gravity()
            #debugging
            #self.printEntries()
            #print "\n"
            #end debugging
            self.randomFillZeroes()
            #debugging
            #self.printEntries()
            #print "\n"
            #end debugging

    def horizontalMonoContaining(self, coords):
        #does self.entries contain a horizontal mono containing the entry coords?
        colour = self.entries[coords[0]][coords[1]]
        l = 0
        while True:
            if (coords[1]+l >= width) or (self.entries[coords[0]][coords[1]+l] != colour):
                break
            else:
                l += 1
        r = 0
        while True:
            if (coords[1] - r < 0) or (self.entries[coords[0]][coords[1]-r] != colour):
                break
            else:
                r += 1
        return l + r - 1 >= vanishLength

    def verticalMonoContaining(self, coords):
        #does self.entries contain a vertical mono containing the entry coords?
        colour = self.entries[coords[0]][coords[1]]
        d = 0
        while True:
            if (coords[0] + d >= height) or (self.entries[coords[0] + d][coords[1]] != colour):
                break
            else:
                d += 1
        u = 0
        while True:
            if (coords[0] - u < 0) or (self.entries[coords[0] - u][coords[1]] != colour):
                break
            else:
                u += 1
        return u + d - 1 >= vanishLength

    def legitMoves(self):
        #moves swap two entries which are adjacent horizontally or vertically. A move is legit iff it creates a new mono
        #this function returns a list of all legit moves, as a list of pairs of coordinates
        output = []
        for i in range(height):
            for j in range(width):
                if (j < width - 1) and (self.entries[i][j] != self.entries[i][j+1]):
                #it makes sense to swap [i,j] and [i,j+1]. does that create a new mono?
                #copy.deepcopy is really slow, so we'll apply the move, test for monos, then apply it again to get back where we started
                    self.applyMove([[i, j], [i, j+1]])
                    #now look for monos. There can be four kinds:
                    # 1. vertical mono containing [i,j+1] of colour entries[i][j]
                    # 2. vertical mono containing [i,j] of colour entries[i][j+1]
                    # 3. horizontal mono finishing at [i,j] of colour entries[i][j+1]
                    # 4. horizontal mono starting at [i,j+1] of colour entries[i][j]
                    if self.verticalMonoContaining([i, j+1]) or self.verticalMonoContaining([i, j]) or self.horizontalMonoContaining([i, j]) or self.horizontalMonoContaining([i, j+1]):
                        output.append([[i, j], [i, j+1]])
                    self.applyMove([[i, j], [i, j+1]]) # get self.entries back to where it was before
                if (i < height - 1) and (self.entries[i][j] != self.entries[i+1][j]):
                    #it makes sense to swap [i,j] and [i+1,j]. does that create a new mono?
                    self.applyMove([[i, j],[i+1, j]])
                    if self.verticalMonoContaining([i, j]) or self.verticalMonoContaining([i+1, j]) or self.horizontalMonoContaining([i, j]) or self.horizontalMonoContaining([i+1, j]):
                        output.append([[i, j], [i+1, j]])
                    self.applyMove([[i, j], [i+1, j]])
        return output

    def applyMove(self, move):
        firstrow = move[0][0]
        firstcol = move[0][1]
        secondrow = move[1][0]
        secondcol = move[1][1]
        temp = self.entries[firstrow][firstcol]
        self.entries[firstrow][firstcol] = self.entries[secondrow][secondcol]
        self.entries[secondrow][secondcol] = temp


#strategies:
        # choose randomly from all available moves
        # choose randomly from highest few moves available
        # choose reandomly from lowest few moves
        # mixed
        # approximate the play that maximises something or other

def testStrategy(chooser, numberOfGames):
    #a strategy is a way of choosing moves. testStrategy takes 
    #a function `chooser' which accepts a list of moves and returns
    #one of them, and a number numberOfGames, and runs numberOfGames
    #games using chooser to pick from the available moves.
    #It returns the list of scores from those games
    scores = []
    for i in range(numberOfGames):
        b = board()
        b.randomize()
        while True:
            b.evolve()
            moves = b.legitMoves()
            if len(moves) == 0:
                scores.append(b.score)
                break
            b.applyMove(chooser(moves))

    mu = sum(scores)/(1.0 * numberOfGames)
    s2 = sum([(x-mu) ** 2 for x in scores])/ (numberOfGames - 1)
    print "n", numberOfGames, "mean", mu, "sd", s2 ** 0.5
    return scores

##########################
# some chooser functions #
##########################

def randomChooser(moves):
    return random.choice(moves)
def chooseFromTop3(moves):
    #pick randomly from the 3 moves nearest the top
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return random.choice(movesSortedByRow[:3])
def chooseFromTop2(moves):
    #pick randomly from the 2 moves nearest the top
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return random.choice(movesSortedByRow[:2])
def chooseTop1(moves):
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    return movesSortedByRow[0]
def chooseFromHighest(moves):
    #pick randomly from the highest moves
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    highestRowWithMoves = movesSortedByRow[0][0][0]
    highestMoves = [movesSortedByRow[0]]
    for i in range(1,len(movesSortedByRow)):
        if movesSortedByRow[i][0][0] == highestRowWithMoves:
            highestMoves.append(movesSortedByRow[i])
        else:
            break
    return random.choice(highestMoves)
def chooseLastHighest(moves):
    movesSortedByRow = sorted(moves, key=lambda x: x[0][0])
    highestRowWithMoves = movesSortedByRow[0][0][0]
    highestMoves = [movesSortedByRow[0]]
    for i in range(1,len(movesSortedByRow)):
        if movesSortedByRow[i][0][0] == highestRowWithMoves:
            highestMoves.append(movesSortedByRow[i])
        else:
            break
    return highestMoves[-1]
def chooseBottom5(moves):
    #pick randomly from the 5 moves nearest the bottom
    movesSortedByRow = sorted(moves, key = lambda x: x[0][0])
    return random.choice(movesSortedByRow[-5:])

####################################
# run the test, export the results #
####################################

scores = testStrategy(chooseFromHighest, 50000)

#export scores data in R-readable format
f = open("/home/mjt/Dropbox/code/python/jewels/chooseFromHighest_scores.txt", "a")
r_string = "\nx=c(" + ",".join(map(str, scores)) + ")"
#use source("scores.txt") in R to load this
f.write(r_string)
f.close()

#mean ~150 for top 3, ~120 for top 5, ~195 for top 2, ~310 for top 1.
#but chooseFromHighest seems to be smaller (weak evidence: n=10000, mean=299.2, sd = 276.2)
#chooseLastHighest: n 10000 mean 299.3363 sd 271.212
#another 10000 run of rightmost gave mean 302.7, sd 276.12
#another 10000 run of top1 gave mean 314.4482, sd 289.886
# It isn't a problem that chooseLastHighest does worse than chooseTop1:
# it isn't picking the rightmost move, because top1 tends to do
# horizontal monos first


# to do: log number of moves available to get an idea of what the sequences look like
# make a mixed strategy that plays near the top, but near the bottom when few moves are available