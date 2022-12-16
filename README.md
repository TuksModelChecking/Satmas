# Satmas

To test the base coalition vs opposition synthesis implementation do the following:

1. Clone this repo
2. Pick a SAT solver to use (CaDiCal, OpenWBO or PicoSAT). CaDiCal should be the fastest.
3. Checkout the branch of the solver you want to use (CaDiCal is on the ```feedback_cadical``` branch, OpenWBO is on the ```feedback_open_gdb``` branch, and PicoSAT is on the ```feedback_old_solver``` branch)
4. Follow the readme in the selected branch to install the selected solver
5. cd into the implementation folder and run the following command to test any of the selected implementations
6. run a test using the command ```python3 logic_encoding.py /full/path/to/input/testfile.yml```