import numpy as np
import matplotlib.pyplot as plt


lims = np.array([0, 1])
N = 100
x0 = 0.1


def f(x):
    # The iterative map function.
    r = 3.1
    return r*x*(1-x)


def sim(x0, f=f, N=N):
    # Generates the first N points of the iterative map f, with the initial
    # condition x0.

    x = np.zeros(N)
    x[0] = x0
    for i in range(1,N):
        x[i] = f(x[i-1])

    return x


def generate_cobweb_points(x):
    # Generates the points for a cobweb plot, for a given input vector x

    # for each iteration we want two lines, one vertical, and one horizontal. 
    # Except for the last iteration, where we just want one vertical line
    points = np.zeros((2, x.size * 2 - 1))

    # Generate x-values. Every element in x should be repeated once. Except for
    # the last element, which shouldn't be repeated.
    points[0,::2] = x
    points[0,1::2] = x[:-1]

    # Generate y-values. Should be like x-values, but shifted by one to the
    # right. The first value is replaced by a zero, and the last value is the
    # same as the second to last
    points[1, 1::2] = x[1:]
    points[1, 2::2] = x[1:]

    return points


def cobweb(x0, f=f, N=N, lims=lims):
    # Function to plot the cobweb plot for a given one-dimensional map and
    # initial condition.

    # Create the figure
    fig, ax = plt.subplots()

    # Perform the simulation and generate cobweb points
    x = sim(x0, f, N)
    points = generate_cobweb_points(x)

    # generating the straight line data and the map function for plotting
    straight_line = np.linspace(*lims, num=100)
    function = f(straight_line)

    # Plotting x, the map function and the cobweb
    ax.plot(straight_line, straight_line, 'k-', linewidth=1)
    ax.plot(straight_line, function, 'k-', linewidth=2)
    ax.plot(points[0], points[1], linewidth=1)

    # Setting limits and showing the plot
    ax.set_xlim(lims)
    ax.set_ylim(lims)

    plt.show()


if __name__ == "__main__":
    cobweb(x0)

