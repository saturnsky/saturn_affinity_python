# Saturn Affinity

Program to optimize cache utilization for games on Ryzen CPUs with multiple L3 cache clusters.

The purpose of this program is to optimize the speed of cache-sensitive games, even when background programs are running.

Additionally, it supports Intel CPUs with both P and E cores. In this case, the only effect is to prevent background programs from reducing the performance of the game.

## Download
* [Saturn Affinity Release Link](https://github.com/saturnsky/saturn_affinity_python/releases)

## How it works (AMD CPU)
1. If a program in the Game List is in the foreground, it is assigned to the cores with access to the largest L3 cache, and all other programs are assigned to the remaining cores.
2. Otherwise, reassign them so that all programs have access to all cores.

## How it works (Intel CPU)
1. If a program in the game list is in the foreground, it is assigned to P-cores and all other programs are assigned to E-cores.
2. Otherwise, reassign them so that all programs have access to all cores.

## What are the effects of this program? (AMD CPU)
![AMD Ryzen 5000 Series Diagram](./docs/zen3.jpg)
Zen 3 and Zen 4 have one L3 cache per CCD, and there is no benefit to having L3 caches on different CCDs.

This program allocates the game being played to CCD0 and all other programs to CCD1, which has the effect of making the L3 cache on CCD0 exclusively used by the game.

CPUs with more L3 cache capacity for CCD0, such as the Ryzen 9 7950X3D and Ryzen 9 7900X3D, will see a greater effect, but in my testing, for cache-sensitive games, the Ryzen 9 5950X also saw a significant effect.

Older generation Ryzen CPUs (such as the Ryzen 7 2700X), which have two CCXs on a single CCD and cannot benefit from caches from different CCXs, are expected to see a similar effect. However, the smaller the L3 cache capacity, the less effective it will be. 

For games that are highly cache-sensitive but weak on multithreading, CPUs with two CCDs and each CCD has two CCXs (such as the Ryzen 9 3950X) may also see performance gains, but many games are expected to experience performance drops due to the quartering of the number of cores allocated.

## What are the effects of this program? (Intel CPU)
![Rapter Lake E-Cores Slide](./docs/rapterlake.png)
Modern Intel CPUs are organized into P-cores for high-performance tasks and E-cores for multi-threaded performance.

This program allocates the game being played to P-cores and all other programs to E-cores, which has the effect of making the P-cores exclusively used by the game.

This will prevent other programs from using P-cores to interfere with the game's scheduling, so expect to see performance improvements when using this program.

## Are there any games that shouldn't use this program?
For games that spawn threads based on the number of cores in your CPU, it's possible that performance will suffer. This tool should not be used in such games.

Even if this is not the case, games that can utilize a large number of threads may experience a performance drop on CPUs with fewer cores.

## Caution
I created this program for the 7950X3D, but have not tested it on a real 7950X3D. Therefore, I cannot guarantee its behavior on the 7950X3D.

For example, the Core Affinity feature in the Ryzen chipset driver may conflict with a feature in this program.

Theoretically, this program extends the functionality to work on modern Intel CPUs, but it has not been tested in an actual Intel CPU environment. Therefore, I cannot guarantee its behavior in this case.

## Compatibility
Theoretically, this program should work on CPUs with multiple L3 cache clusters. It is assumed that the larger the L3 cache cluster, the better the effect.

The program can also be used on CPUs with both P and E cores. In this case, the program will automatically recognize the cores that support hyperthreading as P-cores and the remaining cores as E-cores.

### Tested CPU
- Ryzen 9 5950X (The game exclusively utilizes 8 cores and 32MB of L3 cache)

## Benchmark

### Stellaris
Ryzen 9 5950X, DDR4-3200 128GB, Windows 11 [10.0.22621.1344]

This system is not a clean environment because the operating system has been installed for a very long time, and there are many background programs running, so the effect may be exaggerated compared to a typical PC.

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
