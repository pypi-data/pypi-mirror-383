# Copyright 2025 Artezaru
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# ==========================================================================================
# Time computation evolution of the function core_polynomial
# ------------------------------------------------------------------------------------------
# The time can be change according to the used machine and its current load.
# ==========================================================================================

from pyzernike.core import core_polynomial
import time
import numpy
import matplotlib.pyplot as plt
import os
import csv

# Define a set of Zernike polynomials and their derivatives to test the timing
def up_to_order(order, dr=None, dt=None):
    # Set the default derivative orders if not provided
    if dr is None:
        dr = [0]
    if dt is None:
        dt = [0]
    assert len(dr) == len(dt), "dr and dt must have the same length"

    # Initialize lists to hold the n, m, dr, and dt values
    n_values = []
    m_values = []
    dr_values = []
    dt_values = []

    # Loop through each order from 0 to the specified order
    for n in range(order + 1):
        for m in range(-n, n + 1, 2):  # m takes values from -n to n in steps of 2
            n_values.extend([n] * len(dr))  # Repeat n for each combination of dr/dt
            m_values.extend([m] * len(dr))  # Repeat m for each combination of dr/dt
            dr_values.extend(dr)  # Add all dr values
            dt_values.extend(dt)  # Add all dt values

    return n_values, m_values, dr_values, dt_values


def time_core_polynomial(order, num_points, dr=None, dt=None, flag_radial=True, precompute=True, Nmean=10):
    # Generate the n, m, dr, and dt values for the specified order
    n, m, rho_derivative, theta_derivative = up_to_order(order, dr=dr, dt=dt)

    # Create a grid of rho and theta values
    rho = numpy.random.uniform(0, 1, num_points)
    theta = numpy.random.uniform(0, 2 * numpy.pi, num_points)

    # Record the start time
    start_time = time.perf_counter()

    for _ in range(Nmean):
        # Call the core_create_precomputing_sets function with the generated values
        _ = core_polynomial(
            rho=rho,
            theta=theta,
            n=n,
            m=m,
            rho_derivative=rho_derivative,
            theta_derivative=theta_derivative,
            flag_radial=flag_radial,
            precompute=precompute,
        )

    # Record the end time
    end_time = time.perf_counter()

    # Calculate the elapsed time
    elapsed_time = (end_time - start_time) / Nmean

    return elapsed_time



if __name__ == "__main__":

    Nmean = 5  # Number of repetitions for averaging the time
    orders = [3, 5, 7, 9]
    dr_unique = [0]
    dt_unique = [0]
    dr_first_derivative = [0, 1, 0]
    dt_first_derivative = [0, 0, 1]
    # dr_second_derivative = [0, 1, 0, 1, 2, 0]
    # dt_second_derivative = [0, 0, 1, 1, 0, 2]

    # Create a grid of rho and theta values
    num_points = []
    for power in [3,4,5,6]:
        num_points.extend([10**power, 2*(10**power), 5*(10**power)])
    num_points.append(3000*4000)

    times_unique = []
    times_first = []
    # times_second = []
    for n_points in num_points:
        print(f"Number of points: {n_points} - starting computations...")
        time_unique = [
            time_core_polynomial(order, n_points, dr=dr_unique, dt=dt_unique, Nmean=Nmean)
            for order in orders
        ]
        print("\t unique done")
        time_first = [
            time_core_polynomial(order, n_points, dr=dr_first_derivative, dt=dt_first_derivative, Nmean=Nmean)
            for order in orders
        ]
        print("\t first done")
        # time_second = [
        #     time_core_polynomial(order, n_points, dr=dr_second_derivative, dt=dt_second_derivative, Nmean=Nmean)
        #     for order in orders
        # ]
        # print("\t second done")
        times_unique.append(time_unique)
        times_first.append(time_first)
        # times_second.append(time_second)

    # Plot the results (time versus number of points - log-log scale) 
    #
    # - 1 order = one color
    # - 3 curves per color (unique, first derivative, second derivative) with different line styles
    plt.figure(figsize=(10, 6))
    plt.title
    colors=['blue','red','green','orange','black']
    markers = ['o', 's', '^']
    linestyles = ['-', '--', ':']
    labels = ['Unique', 'First Derivative', 'Second Derivative']
    for i, order in enumerate(orders):
        for j, times in enumerate([times_unique, times_first]):#, times_second]):
            plt.plot(num_points, [t[i] for t in times], label=f"Order {order} - {labels[j]}", color=colors[i], marker=markers[j], linestyle=linestyles[j])
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Number of Points (log scale)")
    plt.ylabel("Time (seconds, log scale)")
    plt.title("Timing of 'core_polynomial' function for all Zernike polynomials up to a given order")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the results in an image file
    file_fig = os.path.join(os.path.dirname(__file__), "results", "timing_core_polynomial.png")
    os.makedirs(os.path.dirname(file_fig), exist_ok=True)
    os.remove(file_fig) if os.path.exists(file_fig) else None
    plt.savefig(file_fig, dpi=300)

    # Save the results in an text csv file
    file_txt = os.path.join(os.path.dirname(__file__), "results", "timing_core_polynomial.csv")
    os.makedirs(os.path.dirname(file_txt), exist_ok=True)
    os.remove(file_txt) if os.path.exists(file_txt) else None
    with open(file_txt, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['Number of Points'] + [f'Order {order} - {label}' for order in orders for label in labels[:2]]
        writer.writerow(header)
        for i, n_points in enumerate(num_points):
            row = [n_points] + [times_unique[i][j] for j in range(len(orders))] + [times_first[i][j] for j in range(len(orders))]
            writer.writerow(row)

    # Show the plot
    plt.show()