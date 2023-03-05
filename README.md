# Saturn Affinity

CPU load balancing program for Ryzen CPUs with multiple CCDs.

The goal is to minimize the impact on game performance while background programs are running.

## How it works
1. If a program in the Game List is in the foreground, assign it to CCD 0 and all other programs to CCD 1.
2. Otherwise, reassign all programs so that they have access to both CCDs 0 and 1.

## Caution
I created this program for the 7950X3D, but have not tested it on a real 7950X3D. Therefore, I cannot guarantee its behavior on the 7950X3D.

For example, the Core Affinity feature in the Ryzen chipset driver may conflict with a feature in this program.

In theory, it should also work on a Ryzen 7900X3D, but I have no plans to test its behavior in that environment.

## Benchmark

### Stellaris
Ryzen 9 5950X, DDR4-3200 128GB, Windows 11 [10.0.22621.1344]

This system is not a clean environment because the operating system has been installed for a very long time, so the effect may be exaggerated compared to a typical PC.

#### Benchmark Settings
- Galaxy Size: Huge (1000)
- Galaxy Shape: Spiral (2 Arms)
- AI Empires: 15
- Advanced AI Stars: 4
- Fallen Empires: 4
- Marauder Empires: 3

#### Benchmark Methods
1. Start the game with the above settings.
2. Save the game.
3. All tests started by loading the game above.
4. Use the human_ai console command.
5. See how many in-game days pass for 5 minutes at fastest speed.
6. Repeat steps 3 to 5 3 times.

#### Before
- 1st: 3112 days
- 2nd: 3118 days
- 3rd: 3113 days

#### After
- 1st: 4696 days
- 2nd: 4662 days
- 3rd: 4695 days

#### Result
50.4% performance improvement.