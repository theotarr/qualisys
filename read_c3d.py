import c3d
import matplotlib.pyplot as plt

reader = c3d.Reader(open('data/pre_walk.c3d', 'rb'))

frames = reader.read_frames()

for i, points, analog in reader.read_frames():
    print('frame {}: point {}'.format(
        i, points.shape))
    
    print (points)
    
    # # Plot the points in 3D
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(points[:, 0], points[:, 1], points[:, 2])
    
    # # Set the same scale for all axes
    # max_range = max(points[:, 0].max() - points[:, 0].min(),
    #                 points[:, 1].max() - points[:, 1].min(),
    #                 points[:, 2].max() - points[:, 2].min())
    # mid_x = (points[:, 0].max() + points[:, 0].min()) * 0.5
    # mid_y = (points[:, 1].max() + points[:, 1].min()) * 0.5
    # mid_z = (points[:, 2].max() + points[:, 2].min()) * 0.5
    # ax.set_xlim(mid_x - max_range * 0.5, mid_x + max_range * 0.5)
    # ax.set_ylim(mid_y - max_range * 0.5, mid_y + max_range * 0.5)
    # ax.set_zlim(mid_z - max_range * 0.5, mid_z + max_range * 0.5)
    
    # plt.show()
    
    
    # print 2 frames
    if i == 2:
        break