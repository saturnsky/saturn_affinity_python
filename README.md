# Saturn Affinity

A CPU load balancing program for the Ryzen 7950X3D.

The goal is to minimize the impact on game performance while background programs are running.

## How it works
1. If a program in the Game List is in the foreground, assign it to CCD 0 and all other programs to CCD 1.
2. Otherwise, reassign all programs so that they have access to both CCDs 0 and 1.

## Caution
This program has not been tested in a Ryzen 7950X3D environment. I believe this program should work in theory, but I cannot guarantee actual behavior.

For example, the Core Affinity feature in the Ryzen chipset driver may conflict with a feature in this program.

In theory, it should also work on a Ryzen 7900X3D, but I have no plans to test its behavior in that environment.