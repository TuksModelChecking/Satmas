# Satmas - Epsilon Nash Equilibrium Extension

The implementation supports two algorithms, an iterative one and a direct one. The tool does rely on the open-wbo Max-SAT solver and does assume the executable
called 'open-wbo_static' is available in the implementation directory.
To run the code follow the steps below:

1. Clone this repo
2. Copy the open-wbo_static executable to the implementation folder.
3. Checkout the branch of the solver you want to use (epsilon-nash)
4. cd into the implementation folder.
5. Install project dependencies with ``` pip install -r requirements.txt ```
6. To execute the program you can run ``` python3 main.py -m iepne -s ./path/to/scenario.yml ```, this will execute the iterative algorithm, to run the direct 
algorithm pass the ``` -m wepne ``` as a flag.


