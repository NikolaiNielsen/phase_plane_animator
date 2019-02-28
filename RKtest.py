#%%
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


# inputs:
# x: np-array, shape (d,n), where d is dimensionality and n is number of 
#    trajectories.
# f: function that calculates the derivatives of x based on parameters p.
# p: object containing the parameters for the function p. For example d,d 
#    matrix for a linear system

p = np.array([[0, -1], [1, 0]])
x0 = np.array([1, 0])
N = 5000
t = np.zeros(N)
dt = 0.02
xlim = np.array([-1, 1]) * 4
ylim = np.array([-1, 1]) * 4
n_skip = 10
e_stop = 0.01

def f(x, p):
    mu = 2
    x1, x2 = x
    # dx = x2
    # dy = mu * (1-x1**2) * x2 - x1
    dx = -x2
    dy = x1
    return np.array((dx, dy))


def rk4(r, t, dt, f, p=None):
    # The four contributions
    k1 = f(r, p)
    k2 = f(r + 0.5*dt*k1, p)
    k3 = f(r + 0.5*dt*k2, p)
    k4 = f(r + dt*k3, p)
    return r + dt * (k1 + 2*k2 + 2*k3 + k4)/6


def get_plot_indices(N, n):
    # Returns a list of indices used for each frame of the animation
    # N: Total number of data points
    # n: number of (new) points to show in each frame
    frames = int(np.ceil(N/n))
    id = np.cumsum(np.ones(frames)*n, dtype=int)
    # If the last entry in id is larger than N, we set it to N, so we dont' get 
    # an index out of bounds error
    if id[-1] > N:
        id[-1] = N
    # And lastly we subtract 1 to account for zero-indexation:
    return id-1


def rka(x, t, dt, err, f, p=None):
    # Adaptive Runge Kutta. Directly lifted from our course in Numerical
    # Methods.
    tSave = t
    xSave = x
    safe1 = 0.9
    safe2 = 4.
    maxTry = 100
    eps = np.finfo(float).eps
    for i in range(maxTry):
        half_dt = dt/2
        xTemp = rk4(xSave, tSave, half_dt, f, p)
        t = tSave + half_dt
        xSmall = rk4(xTemp, t, half_dt, f, p)
        
        t = tSave + dt
        xBig = rk4(xSave, tSave, dt, f, p)

        scale = err  * (np.abs(xSmall) + np.abs(xBig))/2
        xDiff = xSmall - xBig
        errorRatio = np.max( np.abs(xDiff)/(scale + eps))

        dt_old = dt
        dt = safe1*dt_old*errorRatio**(-0.2)
        dt = max(dt, dt_old/safe2)
        dt = min(dt, safe2*dt_old)

        if errorRatio < 1:
            return xSmall, t, dt
    
    raise Exception('Adaptive Runge-Kutta routine failed')


def sim_rk4(f, x0, dt, N, p=None):
    # create our position vector
    x = np.zeros(list(x0.shape) + [N])
    x[:,0] = x0
    # create our time vector
    t = np.cumsum(np.zeros(N)+dt) - dt

    # perform the simulation
    for n in range(1, N):
        x[:,n] = rk4(x[:, n-1], t[n-1], dt, f, p)

        # Calculate the minimum distance to preceeding points. Stop if smaller
        # than e_stop.
        min_dist = get_dists(x[:,n], x[:,:n])
        if min_dist <= e_stop:
            N = n + 1
            return x[:,:N], t[:N]
    return x, t

def get_dists(x, x_pre):
    x_cur = np.atleast_2d(x).T
    return np.amin(np.sqrt(np.sum((x_pre-x_cur)**2, axis=0)))

def min_prec_dist(x):
    # calculates the minimum distance from the current point to preceeding 
    # points
    N = x.shape[1]
    min_dist = np.zeros(N)
    for n in range(1, N):
        x_pre = x[:, :n]
        min_dist[n] = get_dists(x[:,n], x_pre)
    return min_dist


class Animator(object):
    # The animator object, created for every simulation we want to plot
    def __init__(self, fig, ax, x, ids, xlim=(-2, 2), ylim=(-2, 2)):
        # plug stuff into the object and create the empty line
        self.ax = ax
        self.fig = fig
        self.line, = ax.plot([], [], 'k-')
        self.ax.axis('equal')
        self.ax.set_xlim(*xlim)
        self.ax.set_ylim(*ylim)
        self.x = x
        self.N = self.x.shape[1]
        self.frames = ids.size
        self.ids = ids

    def init(self):
        # function to clear the line every time it is plotted (init function 
        # for FuncAnim)
        self.line.set_data([], [])
        return self.line,

    def __call__(self, i):
        # The function for updating the plot
        id = self.ids[i]
        if i == self.frames - 1:
            # on the last step we stop the animation and just plot the finished 
            # product instead
            self.fig.canvas.close_event()
            self.ax.plot(self.x[0], self.x[1], 'k-')
            print('animation done')
        self.line.set_data(self.x[0, :id], self.x[1, :id])
        return self.line,


def on_mouse(event, fig, ax, n_skip, N=N):
    # Pressing the mouse button grabs the x and y position, simulates the 
    # system and animates it.

    # But only if it's a left mouse click
    if event.button != 1: return

    # Grab the initial conditions
    x0 = np.array([event.xdata, event.ydata])

    # simulate with RK4
    x, _ = sim_rk4(f, x0, dt, N, p)
    # Get the new data length
    N = x.shape[1]

    # Get the plot ids
    ids = get_plot_indices(N, n_skip)

    # Instantiate the animator
    A = Animator(fig, ax, x, ids, xlim, ylim)

    # Run the animation
    ani = animation.FuncAnimation(
        fig, A, init_func=A.init, frames=ids.size, interval=2, blit=True,
        save_count=1000,
        repeat=False)
    
    # And remember to draw!
    fig.canvas.draw()

def main(f=f):
    fig, ax = plt.subplots()
    ax.axis('equal')
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    fig.canvas.mpl_connect('button_press_event',
                        lambda event: on_mouse(event, fig=fig, ax=ax, 
                                                n_skip=n_skip))

    plt.show()

if __name__ == "__main__":
    main()