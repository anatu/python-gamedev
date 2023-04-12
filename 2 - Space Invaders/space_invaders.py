'''
Space Invaders

Base Classes
a) Actor (base actor class)
b) GameLayer (custom layer for game logic)

Actors
1) PlayerCannon: Character controlled by the player. <space> to shoot, and 
<left>, <right> to move the cannon horizontally. No vertical movement.
2) Alien: Each of the descending enemies w/ different looks/scores
depending on type
3) AlienColumn: A column of 5 aliens
4) AlienGroup: An entire group of enemies, which moves uniformly
both horizontally as well as down towards the player
5) Shoot: The projectile that the enemies launch at the player
6) PlayerShoot: The projectile that the player launches at the enemies
which we will implement by extending Shoot
'''

import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu

