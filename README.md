# FYP---non-linear-PID-optimisation

This is a project on using a Particle swarm optimisation algorithm to optimise the paramaters of a FOPID controller using a simulation evaluation as a fitness function.

The complete program is run through main.py but the other files have small tests that run if executed.

From the main menu you can start an optimisation, load an existing swarm, save the currently loaded swarm, create animation and summary graphs of the currently loaded swarm and exit the program

The responses do not need to be exact as the responses are loosely matched to the commands.

Starting an optimisation allows you to enter the number of agents and iterations for the swarm, most optimisation is effective after 20 iterations and 20 agents.

save has 2 options, full and partial save. A full save includes the complete history whereas partial only saves the last iteration. many summary graphs will not be effective with partial save swarms

All loaded swarms must be in the saves folder and must be of the format that the program saves as.