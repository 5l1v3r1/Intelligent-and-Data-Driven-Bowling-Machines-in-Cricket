import numpy as np
import MySQLdb
import itertools
import matplotlib
matplotlib.use('qt5agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import matplotlib.animation as animation
import time
import random

'''
Note: The code is not well written. I just wanted to get stuff done. If you have any questions about the code, feel free to ask.
'''

#Loading our wicket image
image_name = 'with_wicket.jpg'
im = np.array(Image.open(image_name), dtype=np.uint8)
fig,ax = plt.subplots(1)
ax.imshow(im,animated=True)

#connecting to mysql database
db = MySQLdb.connect(host="localhost",
					user="",
					passwd="",
					db="")

cursor = db.cursor()

#quering from database
query = "select distinct(bowler),ball_pitched_height,ball_original_height,ball_pitched_side,ball_original_side,ball_speed from runs inner join players on bowler_id=player_id where ball_pitched_height != 0 and wicket = 1 and ball_speed > 65.0 and bowling_hand = 'right-arm bowler'"
cursor.execute(query)

#fetching data
data = cursor.fetchall()
ball_details = []
for d in data:
	ball_details.append([d[1],d[2],d[3],d[4],d[5]])

#choosing a random ball from the balls that had a wicket
myBall = random.choice(ball_details)

#values for our further calculations
pitched_height = 650+(myBall[0]*84.84)
pitched_side = 1050+(myBall[2]*700)
original_height = 650 - (myBall[1]*421.22)
original_side = 1050+(myBall[3]*700)

initialX = 1050+(myBall[2]*700)-230
initialY = 2250

#making a circle
patch_init = plt.Circle((initialX, initialY), 20,color='green', ec='white')

def init_first():
	#defining the start of the cirlce
	patch_init.center = (initialX, initialY)
	ax.add_patch(patch_init)
	return patch_init,

#functions to get information about lines
def getY(x, slope):
	y = slope*x
	return y

def getX(y,slope):
	x = float(y)/float(slope)
	return x

#slope for both lines, initial to where pitched ball and pitched ball to where the ball actually went
slope = float(initialY - pitched_height) / float(initialX - pitched_side)
slopeSecond = float(pitched_height - original_height) / float(pitched_side - original_side)

isPitched = 0

def animate_first(i):
	global isPitched
	x, y = patch_init.center
	otherx, othery = pitched_side,pitched_height

	yChange = float(myBall[4]/10.0)	#speed of the ball

	if y > othery or x < otherx:
		y = y - yChange
		x = x - getX(yChange,slope)
	elif y > original_height:
		if isPitched == 0:
			#sleep for a moment and continue
			time.sleep(0.1)
			isPitched = 1
		y = y - yChange
		x = x - getX(yChange,slopeSecond)
		
	#change the location of the ball
	patch_init.center = (x, y)
	return patch_init,

print original_side,pitched_side
rect = patches.Circle((original_side, original_height), 20.0, color='black')
ax.add_patch(rect)
rect = patches.Circle((pitched_side, pitched_height), 20.0, color='black')
ax.add_patch(rect)


anim2 = animation.FuncAnimation(fig, animate_first, 
							   init_func=init_first, 
							   frames=5000, 
							   interval=1,
							   repeat=False,
							   blit=True)

figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()
