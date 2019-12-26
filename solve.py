"""
This is the main function of the challengesolve python interface.
It is called with 'solve.py <challengenumber> [number-of-runs]'.

see 'solve.py --help' for fast information on how to use this script.
"""

import sys
import time
import _thread
import importlib
import requests

SCRIPT_VERSION = "0.9.1-RC1"

TIMING = {}
METADATA = {'wrong_solution_count': 0,
            'ctf_token': "No token found yet.",
            'threads_running': 0,
            'runs_finished': 0,
            'runs_awaiting': 0}


def print_help():
    """Print the help"""
    sys.stdout.write("solve.py - Python interface for the Morpheus Challenges.\n\n")
    sys.stdout.write("Usage: solve.py <challenge> [runs] [flags...]\t\tRun the solvescript\n")
    sys.stdout.write("       solve.py --help\t\t\t\t\tPrint this help\n")
    sys.stdout.write("       solve.py --version\t\t\t\tPrint version information\n\n")
    sys.stdout.write("Possible flags:\n")
    sys.stdout.write("\t--bench\t\tPrint benchmark information (Set by default with [runs >= 10] )\n")
    sys.stdout.write("\t--nobench\tSuppress benchmark information\n")
    sys.stdout.write("\t--parallel\tUse multithreading to solve every run in parallel.\n"
                     + "\t\t\tThis limits the maximum number of runs to 100 to prevent unwanted ddos.\n")
    return 0


def print_version():
    """Print version information about this script"""
    sys.stdout.write(SCRIPT_VERSION)
    return 0


def start_solve_instance(challenge_number, run_id, solvefile):
    """Start an instance of the solving function"""
    METADATA['threads_running'] += 1
    METADATA['runs_awaiting'] -= 1
    challenge = requests.get("https://cc.the-morpheus.de/challenges/"
                             + str(challenge_number) + "/")
    TIMING['inst_' + str(run_id) + '_start'] = time.time()

    inst_solution = solvefile.solve(challenge.text)

    TIMING['inst_' + str(run_id) + '_end'] = time.time()

    result = requests.post("https://cc.the-morpheus.de/solutions/"
                           + str(challenge_number) + "/",
                           inst_solution)

    if "Error" in result.text:
        METADATA['wrong_solution_count'] += 1
    else:
        METADATA['ctf_token'] = result.text.strip("Success, ").strip(": ")

    METADATA['runs_finished'] += 1
    METADATA['threads_running'] -= 1
    return 0


def setup_solving(challenge_number, challenge_tries, use_multithreading):
    """Setup and initiate the solving process for given challenge."""
    METADATA['runs_awaiting'] = challenge_tries
    solvefile = None
    try:
        solvefile = importlib.import_module('chall' + str(challenge_number))
    except ModuleNotFoundError:
        sys.stderr.write("Solution-File not found.\n")
        return 1
    TIMING['total_mindelta'] = 1000000
    TIMING['total_maxdelta'] = -1
    TIMING['total_delta'] = 0
    TIMING['total_start_time'] = time.time()
    for i in range(challenge_tries):
        if use_multithreading:
            _thread.start_new_thread(start_solve_instance, (challenge_number, i, solvefile))
        else:
            sys.stderr.write("\rRunning Challenge " + str(challenge_number) + " #" + str(i + 1))
            start_solve_instance(challenge_number, i, solvefile)
    TIMING['total_end_time'] = time.time()
    while METADATA['threads_running'] > 0 or METADATA['runs_awaiting'] > 0:
        sys.stdout.write("\r" + str(METADATA['runs_awaiting']) + "/" + str(METADATA['threads_running']) + "/" + str(METADATA['runs_finished']) + "\t")
    if use_multithreading:
        sys.stdout.write("\r" + str(METADATA['runs_awaiting']) + "/" + str(METADATA['threads_running']) + "/" + str(METADATA['runs_finished']) + "\t")
    return 0


def print_results(challenge_number, challenge_tries, use_benchmarking):
    """Print concluding results and statistics of all runs."""
    sys.stdout.write("\n---------------------------------------------------\n")
    sys.stdout.write("Ergebnisse für Challenge  " + str(challenge_number) + ":\n\n")
    sys.stdout.write("Anzahl der Versuche:      " + str(challenge_tries) + "\n")
    sys.stdout.write("Anzahl der Fehlversuche:  " + str(METADATA['wrong_solution_count']) + "\n")
    sys.stdout.write("Token:                    " + str(METADATA['ctf_token']) + "\n")
    if use_benchmarking:
        TIMING['total_runtime'] = TIMING['total_end_time'] - TIMING['total_start_time']
        for i in range(challenge_tries):
            TIMING['inst_' + str(i) + '_delta'] = TIMING['inst_' + str(i) + '_end'] - TIMING['inst_' + str(i) + '_start']
            TIMING['total_delta'] += TIMING['inst_' + str(i) + '_delta']
            if TIMING['inst_' + str(i) + '_delta'] > TIMING['total_maxdelta']:
                TIMING['total_maxdelta'] = TIMING['inst_' + str(i) + '_delta']
            if TIMING['inst_' + str(i) + '_delta'] < TIMING['total_mindelta']:
                TIMING['total_mindelta'] = TIMING['inst_' + str(i) + '_delta']
        TIMING['total_quotdelta'] = TIMING['total_delta'] / challenge_tries
        sys.stdout.write("\nBenchmark-Laufzeit:       " + f'{(TIMING["total_runtime"]*1000):.5f}' + " ms\n")
        sys.stdout.write("Lösungs-Laufzeit:         " + f'{(TIMING["total_delta"]*1000):.5f}' + " ms\n")
        sys.stdout.write("Kürzeste Laufzeit:        " + f'{(TIMING["total_mindelta"]*1000):.5f}' + " ms\n")
        sys.stdout.write("Längste Laufzeit:         " + f'{(TIMING["total_maxdelta"]*1000):.5f}' + " ms\n")
        sys.stdout.write("Durchschnitts-Laufzeit:   " + f'{(TIMING["total_quotdelta"]*1000):.5f}' + " ms\n")
    sys.stdout.write("---------------------------------------------------\n")
    return 0


def main():
    """Main function of the solvefunction"""

    challenge_number = None
    challenge_tries = 1
    use_benchmarking = False
    use_multithreading = False

    if len(sys.argv) < 2:
        sys.stderr.write("See help: " + sys.argv[0] + " --help")
        return 1
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        return print_help()
    if sys.argv[1] == "--version":
        return print_version()
    if not sys.argv[1].isdigit():
        sys.stderr.write("Error: First argument needs to be a Challenge-ID\n")
        sys.stderr.write("See 'solve.py --help' for more information.\n")
        return 1
    challenge_number = int(sys.argv[1])
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        challenge_tries = int(sys.argv[2])
        if challenge_tries >= 10:
            use_benchmarking = True

    """if len(sys.argv) > 3 and sys.argv[3] == "--bench":
        use_benchmarking = True
    elif len(sys.argv) > 3 and sys.argv[3] == "--nobench":
        use_benchmarking = False"""

    if len(sys.argv) > 3:
        for arg in sys.argv[3:]:
            if arg == "--bench":
                use_benchmarking = True
            if arg == "--nobench":
                use_benchmarking = False
            if arg == "--parallel":
                use_multithreading = True
                if challenge_tries > 100:
                    challenge_tries = 100
                    sys.stdout.write("[WARNING] With multithreading active, you can only process a maximum of 100 runs. Capping down...\n")

    if setup_solving(challenge_number, challenge_tries, use_multithreading) != 0:
        return 1
    print_results(challenge_number, challenge_tries, use_benchmarking)

    return 0


if __name__ == "__main__":
    exit(main())
