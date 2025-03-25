from game import Agent
from game import Actions
from game import Directions
import random
from util import manhattanDistance
import util
import os

class GhostAgent( Agent ):
  def __init__( self, index ):
    self.index = index
    self.target_pos = (7,7)


  def getAction( self, state, target = (1,1) ):

    dist = self.getDistribution(state, target = target )
    #dist = self.getDistributionNeast(state)
    
    if len(dist) == 0: 
      return Directions.STOP, dist
    else:
      return util.chooseFromDistribution( dist ), dist

  def getDistribution(self, state):
    "Returns a Counter encoding a distribution over actions from the provided state."
    util.raiseNotDefined()

class RandomGhost( GhostAgent ):
  "A ghost that chooses a legal action uniformly at random."
  def getDistribution( self, state ):
    dist = util.Counter()
    for a in state.getLegalActions( self.index ): dist[a] = 1.0
    dist.normalize()
    return dist


def calculate_distance_and_coordinates(start, end):
    """
    計算在有牆壁限制的地圖中，兩點之間的最短距離和座標序列。

    Args:
        map_data (list of str): 地圖的二維字串列表，'%' 代表牆壁，其他字元代表可通過。
        start (tuple): 起始座標 (x, y)。
        end (tuple): 終點座標 (x, y)。

    Returns:
        tuple: (最短距離, 座標序列)，如果無法到達則返回 (-1, [])。
    """

    map_data = [
        "%%%%%%%%%%%%%%%%%%%%",
        "%o...%........%....%",
        "%.%%.%.%%%%%%.%.%%.%",
        "%.%..............%.%",
        "%.%.%%.%%  %%.%%.%.%",
        "%......%    %......%",
        "%.%.%%.%%%%%%.%%.%.%",
        "%.%..............%.%",
        "%.%%.%.%%%%%%.%.%%.%",
        "%....%........%...o%",
        "%%%%%%%%%%%%%%%%%%%%"
    ]

    rows = len(map_data)
    cols = max(len(row) for row in map_data)
    queue = [((start), 0, [start])]
    visited = {start}

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        (x, y), distance, path = queue.pop(0)

        if (x, y) == end:
            return distance, path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if 0 <= nx < cols and 0 <= ny < rows:
                if 0 <= ny < rows and 0 <= nx < len(map_data[rows - 1 - ny]) and map_data[rows - 1 - ny][nx] != '%' and (nx, ny) not in visited:
                    queue.append(((nx, ny), distance + 1, path + [(nx, ny)]))
                    visited.add((nx, ny))

    return 0, []


class DirectionalGhost( GhostAgent ):
  "A ghost that prefers to rush Pacman, or flee when scared."
  def __init__( self, index, prob_attack=0.8, prob_scaredFlee=0.8 ):
    self.index = index
    self.prob_attack = prob_attack
    self.prob_scaredFlee = prob_scaredFlee

  def getPosition(self, state):
    return state.getGhostPosition( self.index )
  
  def getDistribution( self, state, target = (1,1) ):  
    # Read variables from state
    
    ghostState = state.getGhostState( self.index )
    legalActions = state.getLegalActions( self.index )

    pos = state.getGhostPosition( self.index )
    isScared = ghostState.scaredTimer > 0
    
    speed = 1
    if isScared: speed = 0.5
    
    actionVectors = [Actions.directionToVector( a, speed ) for a in legalActions]#可以移動的方向
    newPositions = [( int(pos[0]+a[0]), int(pos[1]+a[1]) ) for a in actionVectors]

    #改成 AI 預測方向
    pacmanPosition = target#state.getPacmanPosition()

    #print('ghost pos',pos, 'target pos',pacmanPosition)

    # Select best actions given the state
    #distancesToPacman = [manhattanDistance( pos, pacmanPosition ) for pos in newPositions]
    #計算可以移動的方向中, 距離 PACMAN 的方向
    distancesToPacman = [calculate_distance_and_coordinates( pos, pacmanPosition ) for pos in newPositions]
    #print('distancesToTarget',distancesToPacman,target)
    
    if isScared:
      bestScore = max( distancesToPacman )
      bestProb = self.prob_scaredFlee
    else:
      bestScore = min( distancesToPacman )
      bestProb = self.prob_attack

    #print( 'ghost', self.index , '位置', newPositions )
    #print( 'PACman 位置', pacmanPosition , '距離' , distancesToPacman )
    #print( 'legalActions', legalActions )

    #for idx, gpos in enumerate(newPositions):
    #  distance_ghost1_pacman, path_ghost1_pacman = calculate_distance_and_coordinates(gpos,pacmanPosition)
    #  print(idx,'ghost_pacman',distance_ghost1_pacman, path_ghost1_pacman)

    bestActions = [action for action, distance in zip( legalActions, distancesToPacman ) if distance == bestScore]
    #print('bestActions',bestActions)
    
    # Construct distribution
    dist = util.Counter()
    for a in bestActions: dist[a] = bestProb / len(bestActions)
    for a in legalActions: dist[a] += ( 1-bestProb ) / len(legalActions)
    dist.normalize()

    #print('DirectionalGhost', bestScore, bestProb, dist)
    #print()
    
    return dist
  
  def getDistributionNeast( self, state, newPosition = "" ):
    # Read variables from state

    print('getDistributionNeast')

    ghostState = state.getGhostState( self.index )
    legalActions = state.getLegalActions( self.index )

    pos = state.getGhostPosition( self.index )
    isScared = ghostState.scaredTimer > 0
    
    speed = 1
    if isScared: speed = 0.5

    print('legalActions',legalActions)
    
    actionVectors = [Actions.directionToVector( a, speed ) for a in legalActions]
    newPositions = [( int(pos[0]+a[0]), int(pos[1]+a[1]) ) for a in actionVectors]
    pacmanPosition = state.getPacmanPosition()

    distancesToPacman = []

    distance_ghost1_pacman, path_ghost1_pacman = calculate_distance_and_coordinates(pos,pacmanPosition)
    distancesToPacman.append(distance_ghost1_pacman)
    print(self.index ,'ghost_pacman',distance_ghost1_pacman,path_ghost1_pacman)

    #print('legalActions',legalActions)
    #print('actionVectors',actionVectors)

    # Select best actions given the state
    #distancesToPacman = [manhattanDistance( pos, pacmanPosition ) for pos in newPositions]
    #print(type(distancesToPacman))
    #distancesToPacman = 

    if isScared:
      bestScore = max( distancesToPacman )
      bestProb = self.prob_scaredFlee
    else:
      bestScore = min( distancesToPacman )
      bestProb = self.prob_attack

    #print( 'ghost', self.index , '位置', newPositions )
    #print( 'PACman 位置', pacmanPosition , '距離' , distancesToPacman )
    #print( 'legalActions', legalActions )



    bestActions = [action for action, distance in zip( legalActions, distancesToPacman ) if distance == bestScore]
    #print('bestActions',bestActions)
    
    # Construct distribution
    dist = util.Counter()
    print('bestActions',dist)
    for a in bestActions: dist[a] = bestProb / len(bestActions)
    for a in legalActions: dist[a] += ( 1-bestProb ) / len(legalActions)
    dist.normalize()

    #dist = {'West': 1.0}
    #print('DirectionalGhost', bestScore, bestProb, dist)
    print('dist',dist,type(dist))
    print()
    
    return dist
