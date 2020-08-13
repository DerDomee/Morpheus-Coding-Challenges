#!/bin/python
"""
This is the main function of the challengesolve python interface.
It is called with 'solve.py <challengenumber> [number-of-runs]'.

see 'solve.py --help' for fast information on how to use this script.

Exit Codes:
    0: Success or no action required or action aborted in interactive mode
  101: Error while parsing arguments (in method parse_arguments() )
  102: Error while checking integrity of arguments
       (in method check_arguments() )
  103: System error while creating threads
  104: No internet connection while trying to fetch challenges
       or push solutions.
  105: A solution file is invalid, the import failed, it doesnt provide a valid
       JSON to push to solution server or other error inside the solution file.
  106: Unknown Error.
"""

import sys
import time
import _thread
import importlib
import requests

SCRIPT_VERSION = "1.0.0"


def print_help():
    """Print the help"""

    # This String looks very proprietary. It is just formatted in a way that
    # It doesnt exceed the 80 char limit in terminal output as well as in code.
    # Sorry for this mess, but it is very clean in terminal output.
    helpstr = "solve.py " + SCRIPT_VERSION + " - Python interface for the " \
              "Morpheus Coding Challenges\n\n" \
              "Usage: solve.py <challenge> [runs] [flags...]\t" \
              "Runs the solvescript\n       solve.py --help\t\t\t\tPrint " \
              "this help and exit\n       solve.py --version\t\t\tPrint " \
              "version information and\n\t\t\t\t\t\texit\n\n" \
              "Possible flags:\n\t--bench\t\tPrint benchmark information\n" \
              "\t--interactive\tBefore solving the challenges, print the " \
              "parsed\n\t\t\truntime-settings and ask if user wants to " \
              "proceed\n\t--parallel\tUse multithreading to solve every run " \
              "in parallel.\n\t\t\tThis limits the maximum number of runs " \
              "to 100 to \n\t\t\tprevent rate limit crashing.\n\t" \
              "--save-res\tSave all results as JSON to a file. No filename\n" \
              "\t\t\tis needed, as this script creates a new file with" \
              "\n\t\t\tcurrent timestamp as name.\n"

    sys.stdout.write(helpstr)
    return 0


def print_version():
    """Print version information about this script"""
    sys.stdout.write(SCRIPT_VERSION + "\n")
    return 0


def is_integer(n):
    """ Helper function. Returns true if the given argument is an integer.
    """
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def prompt_yes_no(question, default=None):
    """ Helper function. Prompts the user a yes/no question and returns
        True or false depending on the input
    """
    valid = {
        "y": True,
        "yes": True,
        "ye": True,
        "n": False,
        "no": False}

    if default == "yes":
        prompt = "[Y/n]"
    elif default == "no":
        prompt = "[y/N]"
    elif default is None:
        prompt = "[y/n]"
    else:
        raise ValueError("Invalid default answer: '" + default + "'")

    while True:
        sys.stdout.write(question + " " + prompt + " ")
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stderr.write(
                "Please respond with 'Y' or 'N' only. "
                + "(Or with yes/no)\n")


def parse_arguments():
    """ Parses given arguments from a stack and returns a
        dictionary with given settings
    """
    run_args = {
        'raw_arguments': sys.argv[1:],
        'parallel_mode': False,
        'run_interactive': False,
        'interactive_mode': False,
        'benchmark_mode': False,
        'save_raw_results': False}

    challenge_defined = False
    runs_defined = False

    arg_stack = sys.argv[1:]
    arg_errored = False

    def print_unknown_argument():
        sys.stderr.write(
            "Error parsing argument '" + argument_instance
            + "' at index " + str(i + 1) + ": Unknown argument.\n")
        arg_errored = True

    def print_double_argument():
        sys.stderr.write(
            "Warning parsing argument '" + argument_instance
            + "' at index " + str(i + 1)
            + ": Double argument. (Proceeding...)\n")

    def print_illegal_argument():
        sys.stderr.write(
            "Error parsing argument '" + argument_instance
            + "' at index " + str(i + 1)
            + ": Illegal argument or syntax.\n")
        arg_errored = True

    def print_illegal_help_argument():
        sys.stderr.write(
            "Error parsing argument '--help' at index "
            + str(i + 1) + ": This must be the first argument.\n")
        arg_errored = True

    for i in range(len(arg_stack)):
        argument_instance = arg_stack.pop(0)
        if is_integer(argument_instance) and not challenge_defined:
            run_args['challenge_number'] = int(argument_instance)
            challenge_defined = True
            continue
        elif is_integer(argument_instance) and not runs_defined:
            run_args['runs_number'] = int(argument_instance)
            runs_defined = True
            continue
        elif is_integer(argument_instance) and runs_defined and \
                challenge_defined:
            print_unknown_argument()
            arg_errored = True
            continue
        elif argument_instance == "--help":
            if i == 0:
                print_help()
                sys.exit(0)
            else:
                print_illegal_help_argument()
                arg_errored = True
            continue
        elif argument_instance == "--version":
            if i == 0:
                print_version()
                sys.exit(0)
        elif argument_instance == "--parallel":
            if run_args['parallel_mode']:
                print_double_argument()
            run_args['parallel_mode'] = True
            continue
        elif argument_instance == "--interactive":
            if run_args['interactive_mode']:
                print_double_argument()
            run_args['interactive_mode'] = True
            continue
        elif argument_instance == "--bench":
            if run_args['benchmark_mode']:
                print_double_argument()
            run_args['benchmark_mode'] = True
            continue
        elif argument_instance == "--save-res":
            if run_args['save_raw_results']:
                print_double_argument()
            run_args['save_raw_results'] = True
            continue
        else:
            print_unknown_argument()
            arg_errored = True
            continue

    if(arg_errored):
        sys.exit(101)

    return run_args


def check_arguments(run_args):
    """ Check for logical errors in the argument dictionary.
    """
    checking_errored = False

    def print_illegal_state(custom_message="Unknown error"):
        sys.stderr.write("Error checking arguments: " + custom_message + "\n")

    def print_warning_state(custom_message="Unknown warning"):
        sys.stderr.write("Warning checking arguments: " + custom_message
                         + " (Proceeding...)\n")

    if "challenge_number" not in run_args:
        print_illegal_state("No challenge number defined.")
        checking_errored = True

    if "runs_number" not in run_args:
        run_args['runs_number'] = 1

    if "challenge_number" in run_args and run_args['challenge_number'] < 1:
        print_illegal_state("The Challenge ID must not be 0 or negative.")
        checking_errored = True

    if "runs_number" in run_args and run_args['runs_number'] < 1:
        print_illegal_state("The number of runs can not be 0 or negative.")
        checking_errored = True

    if "runs_number" in run_args and run_args['runs_number'] == 1 and \
            run_args['benchmark_mode']:
        print_warning_state("Benchmarking only makes sense with more than 1 "
                            + "run. Turning off benchmark mode.")
        run_args['benchmark_mode'] = False

    if "runs_number" in run_args and run_args['runs_number'] > 100 and \
            run_args['parallel_mode']:
        print_warning_state("Parallel mode limits the maximum amount "
                            + "of runs to 100 to prevent rate limit crashing. "
                            + "Applying limit.")
        run_args['runs_number'] = 100

    if checking_errored:
        sys.exit(102)


def interactive_pass(run_args):
    """ If interactive mode is enabled, pretty-print argument dictionary
        and ask user if he wants to proceed.
    """
    if not run_args['interactive_mode']:
        return

    setstr = "--------------------"
    setstr += "\nChallenge to run: {}".format(run_args['challenge_number'])
    setstr += "\nNumber of runs: {}".format(run_args['runs_number'])
    setstr += "\nParallel Mode: {}".format(run_args['parallel_mode'])
    setstr += "\nBenchmark Mode: {}".format(run_args['benchmark_mode'])
    setstr += "\nSave results in file: {}".format(run_args['save_raw_results'])
    setstr += "\n--------------------"
    sys.stdout.write(setstr + "\n\n")

    if not prompt_yes_no("Do you want to proceed?", "yes"):
        sys.exit(0)


def solve_instance(run_args, run_data, timing_data, i, solvefile):
    run_data['runs_in_progress'] += 1
    run_data['runs_awaiting'] -= 1

    timing_instance = {
        'total_start': time.time()}

    challenge = requests.get(
        "https://cc.the-morpheus.de/challenges/"
        + str(run_args['challenge_number']) + "/")

    timing_instance['runtime_start'] = time.time()
    solution_instance = solvefile.solve(challenge.text)
    timing_instance['runtime_end'] = time.time()

    solution_result = requests.post(
        "https://cc.the-morpheus.de/solutions/"
        + str(run_args['challenge_number']) + "/",
        solution_instance)

    if "Error" in solution_result.text:
        run_data['wrong_solutions'] += 1
    else:
        if run_data['ctf_token'] is None:
            ctf_token = solution_result.text.strip("Success, ").strip(": ")
            run_data['ctf_token'] = ctf_token

    timing_instance['total_end'] = time.time()

    t_key = "c" + str(run_args['challenge_number']) + "r" + str(i)
    timing_data[t_key] = timing_instance

    run_data['runs_finished'] += 1
    run_data['runs_in_progress'] -= 1

    return


def solve_challenges(run_args):
    """ Take the argument dictionary and run the challenges
        with the given settings.
    """
    run_data = {
        'runs_awaiting': run_args['runs_number'],
        'runs_in_progress': 0,
        'runs_finished': 0,
        'wrong_solutions': 0,
        'ctf_token': None}

    timing_data = {
        'total_start_time': time.time()}

    solvefile = None

    try:
        solvefile = importlib.import_module(
            'challenges.chall' + str(run_args['challenge_number']))
    except ModuleNotFoundError:
        sys.stderr.write("Error while starting solving of challenges: "
                         + "This Challenge has no corresponding "
                         + "solution file.\n")
        sys.exit(105)

    for i in range(run_args['runs_number']):
        if(run_args['parallel_mode']):
            _thread.start_new_thread(
                solve_instance,
                (run_args, run_data, timing_data, i, solvefile))
        else:
            sys.stdout.write("\rRunning Loop " + str(i + 1))
            solve_instance(run_args, run_data, timing_data, i, solvefile)

    while run_data['runs_in_progress'] or run_data['runs_awaiting']:
        pass

    timing_data['total_end_time'] = time.time()

    result_data = {
        'run_data': run_data,
        'timing_data': timing_data}

    sys.stdout.write("\n")
    return result_data


def parse_result(run_args, run_result):
    """ Parse the results of all runs and create statistics
    """

    timing_data = run_result['timing_data']
    run_data = run_result['run_data']

    statistics = {
        'total_delta': 0,
        'runtime_delta': 0,
        'total_quotdelta': 0,
        'runtime_quotdelta': 0,
        'best_inst_totaldelta': 1000000,
        'worst_inst_totaldelta': -1,
        'best_inst_rundelta': 1000000,
        'worst_inst_rundelta': -1}

    for i in range(run_args['runs_number']):
        key = "c" + str(run_args['challenge_number']) + "r" + str(i)
        timing_data[key]['total_delta'] = timing_data[key]['total_end'] - \
            timing_data[key]['total_start']
        if timing_data[key]['total_delta'] > \
                statistics['worst_inst_totaldelta']:
            statistics['worst_inst_totaldelta'] = \
                timing_data[key]['total_delta']

        if timing_data[key]['total_delta'] < \
                statistics['best_inst_totaldelta']:
            statistics['best_inst_totaldelta'] = \
                timing_data[key]['total_delta']

        timing_data[key]['run_delta'] = timing_data[key]['runtime_end'] - \
            timing_data[key]['runtime_start']

        if timing_data[key]['run_delta'] > \
                statistics['worst_inst_rundelta']:
            statistics['worst_inst_rundelta'] = timing_data[key]['run_delta']

        if timing_data[key]['run_delta'] < \
                statistics['best_inst_rundelta']:
            statistics['best_inst_rundelta'] = timing_data[key]['run_delta']

        statistics['runtime_delta'] += timing_data[key]['run_delta']
        statistics['total_delta'] += timing_data[key]['total_delta']

    statistics['total_quotdelta'] = statistics['total_delta'] / \
        run_args['runs_number']
    statistics['runtime_quotdelta'] = statistics['runtime_delta'] / \
        run_args['runs_number']

    return statistics


def print_result(run_args, run_result, statistics):
    """ Print results of the solving process.
        If benchmarking is enabled, print further information.
    """
    print("\n------------------------------------------------------------")
    print(
        "Ergebnisse für Challenge "
        + str(run_args['challenge_number']) + "\n")
    print(
        "Anzahl der Versuche: "
        + str(run_args['runs_number']))
    print(
        "Anzahl der Fehlversuche: "
        + str(run_result['run_data']['wrong_solutions']))
    print(
        "CTF-Token: "
        + str(run_result['run_data']['ctf_token']))
    if(run_args['benchmark_mode']):
        print()
        print(
            "                      Benchmark-Laufzeit: "
            + str(round(statistics['total_delta'] * 1000, 6))
            + "ms")
        print(
            "                        Lösungs-Laufzeit: "
            + str(round(statistics['runtime_delta'] * 1000, 6))
            + "ms\n")
        print(
            "         Kürzeste totale Instanzlaufzeit: "
            + str(round(statistics['best_inst_totaldelta'] * 1000, 6))
            + "ms")
        print(
            "          Längste totale Instanzlaufzeit: "
            + str(round(statistics['worst_inst_totaldelta'] * 1000, 6))
            + "ms")
        print(
            "Durchschnittliche totale Instanzlaufzeit: "
            + str(round(statistics['total_quotdelta'] * 1000, 6))
            + "ms\n")
        print(
            "                Kürzeste Instanzlaufzeit: "
            + str(round(statistics['best_inst_rundelta'] * 1000, 6))
            + "ms")
        print(
            "                 Längste Instanzlaufzeit: "
            + str(round(statistics['worst_inst_rundelta'] * 1000, 6))
            + "ms")
        print(
            "       Durchschnittliche Instanzlaufzeit: "
            + str(round(statistics['runtime_quotdelta'] * 1000, 6))
            + "ms")
    print("------------------------------------------------------------")


def main():
    """ Literally just the main function. Self explaining.
    """
    run_args = parse_arguments()
    check_arguments(run_args)
    interactive_pass(run_args)
    run_result = solve_challenges(run_args)
    statistics = parse_result(run_args, run_result)
    print_result(run_args, run_result, statistics)
    return 0


if __name__ == "__main__":
    exit(main())
