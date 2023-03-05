# Saturn Affinity

CPU load balancing program for Ryzen CPUs with multiple CCDs.

The goal is to minimize the impact on game performance while background programs are running.

## How it works
1. If a program in the Game List is in the foreground, assign it to CCD 0 and all other programs to CCD 1.
2. Otherwise, reassign all programs so that they have access to both CCDs 0 and 1.

## What are the effects of this program?
![AMD Ryzen 5000 Series Diagram](./docs/zen3.jpg)
Zen 3 and Zen 4 have one L3 cache per CCD, and there is no benefit to having L3 caches on different CCDs.

This program allocates the game being played to CCD0 and all other programs to CCD1, which has the effect of making the L3 cache on CCD0 monopolized by the game.

CPUs with more L3 cache capacity for CCD0, such as the Ryzen 9 7950X3D and Ryzen 9 7900X3D, will see a greater effect, but in my testing, for cache-sensitive games, the Ryzen 9 5950X also saw a significant effect.

## Are there any games that shouldn't use this program?
For games that spawn threads based on the number of cores in your CPU, it's possible that performance will suffer. This tool should not be used in such games.

## Caution
I created this program for the 7950X3D, but have not tested it on a real 7950X3D. Therefore, I cannot guarantee its behavior on the 7950X3D.

For example, the Core Affinity feature in the Ryzen chipset driver may conflict with a feature in this program.

In theory, it should also work on a Ryzen 7900X3D, but I have no plans to test its behavior in that environment.

## Compatibility
Theoretically works on Zen 3 and later architectures with multiple CCDs.

Therefore, CPUs not listed below will not be able to benefit from this tool.

### Tested CPU
- Ryzen 9 5950X

### CPUs that should theoretically work
- Ryzen 9 5900X
- Ryzen 9 7900X
- Ryzen 9 7950X
- Ryzen 9 7900X3D
- Ryzen 9 7950X3D

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