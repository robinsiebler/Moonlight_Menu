#!/usr/bin/python

"""
Moonlight Menu

Usage:
	mmenu.py [-c COLUMNS] [-r ROWS]

Options:
    -h --help       Show this screen.
    -c COLUMNS      Number of columns to display
    -r ROWS         Number of rows to display
"""

import math
import os
import subprocess
import sys

from colorama import Fore, Style, init
from docopt import docopt
from itertools import islice
from pyparsing import OneOrMore, Word, Literal, nums, restOfLine

# pyparsing expressions
game_expr = (OneOrMore(Word(nums) + Literal('. '))).suppress() + restOfLine().setResultsName('Game_Name')
index_expr = (OneOrMore(Word(nums)))


def chunk(it, size):
	"""return the given iterable object in checks of the specified size.

	:param obj it: An iterable object
	:param int size: The maximum size of each chunk

	:return:  A list of lists
	:rtype: list
	"""
	it = iter(it)
	return iter(lambda: tuple(islice(it, size)), ())


def get_choice(list_of_games, num_games, num_pages=None, current_page=None):
	"""get the choice from the user.

	:param list list_of_games:
		The list of games to choose from
	:param int num_games:
		The number of games to choose from
	:param int num_pages:
		The number of pages (of choices) to display
	:param int current_page:
		The currently displayed page number

	:returns: Either an int representing the index of the chosen game or an alpha representing a program choice
	:rtype: obj
	"""
	if current_page == 0:
		text = Fore.WHITE + 'Options: Display (' + Fore.GREEN + 'N' + Fore.WHITE + ')ext page, (' + Fore.MAGENTA + \
		       'C' + Fore.WHITE + ')urrent page, (' + Fore.RED + 'Q' + Fore.WHITE + ')uit or enter the ' + Fore.CYAN + \
		       'Number' + Fore.WHITE + ' of the game to play'
	else:
		text = Fore.WHITE + 'Options: Display (' + Fore.BLUE + 'P' + Fore.WHITE + ')revious page, (' + Fore.GREEN + \
		       'N' + Fore.WHITE + ')ext page, (' + Fore.MAGENTA + 'C' + Fore.WHITE + ')urrent page, (' + \
		       Fore.RED + 'Q' + Fore.WHITE + ')uit or enter the ' + Fore.CYAN + 'Number' + Fore.WHITE + ' of the game to play'

	print '\n' + text
	index = raw_input(Fore.WHITE + Style.BRIGHT + 'What would you like to do?: ').lower()
	while index != 'p' or index != 'n' or index != 'd' or index.isdigit():
		if index == 'c':
			os.system('clear')
			if num_pages:
				list_columns(list_of_games)
				print '\nDisplaying page {} of {}'.format(current_page, num_pages)
			else:
				list_columns(list_of_games)
			print text
		elif index == 'p':
			break
		elif index == 'n':
			break
		elif index == 'q':
			sys.exit()
		elif index.isdigit():
			if 0 < int(index) < num_games:
				break
			else:
				print Fore.RED + '\nSorry that is not a valid choice!'
			print text
		index = raw_input(Fore.WHITE + Style.BRIGHT + 'What would you like to do?: ')

	return index


def list_columns(obj, cols=2, columnwise=True, gap=4):
	"""
	Print the given list in evenly-spaced columns.

	Parameters
	----------
	:param list obj:
		The list to be printed.
	:param int cols:
		The number of columns in which the list should be printed.
	:param bool columnwise: default=True
		If True, the items in the list will be printed column-wise.
		If False the items in the list will be printed row-wise.
	:param int gap:
		The number of spaces that should separate the longest column
		item/s from the next column. This is the effective spacing
		between columns based on the maximum len() of the list items.
	"""

	sobj = [str(item) for item in obj]
	if cols > len(sobj): cols = len(sobj)
	max_len = max([len(item) for item in sobj])
	if columnwise: cols = int(math.ceil(float(len(sobj)) / float(cols)))
	plist = [sobj[i: i + cols] for i in range(0, len(sobj), cols)]
	if columnwise:
		if not len(plist[-1]) == cols:
			plist[-1].extend([''] * (len(sobj) - len(plist[-1])))
		plist = zip(*plist)
	printer = '\n'.join([
		''.join([c.ljust(max_len + gap) for c in p])
		for p in plist])
	print printer


def main(args):
	num_cols = num_rows = lines = 0

	if args['-c'] is not None:
		num_cols = int(args['-c'])
	else:
		num_cols = 2
	if args['-r'] is not None:
		num_rows = int(args['-r'])
	else:
		num_rows = 25

	init()  # innitialize colorama

	# get rid of the output we don't need
	output = subprocess.check_output(['/usr/bin/moonlight', 'list']).split('\n')
	if output[0] == 'Searching for server...':
		output.pop(0)
	if 'Connect to ' in output[0]:
		output.pop(0)

	display_page = None
	foo = None
	index = 0
	game_list = []
	result_list = []

	# get the list of games (striping the soon to be invalid numbers)
	for line in output:
		if line == '':
			pass
		else:
			result = game_expr.parseString(line)
			result_list.append(result['Game_Name'])

	result_list.sort()
	# renumber the game list
	for index, value in enumerate(result_list, start=1):
		game_list.append(str(index) + '. ' + value)

	lines = len(game_list) / num_cols
	os.system('clear')
	if len(game_list) <= lines:
		list_columns(game_list, num_cols)
		index = get_choice(game_list, len(game_list))
	else:
		index = 'a'
		current_page = 0
		foo = list(chunk(game_list, num_rows * num_cols))
		num_pages = len(foo)
		while not index.isdigit():
			list_columns(list(foo[current_page]), num_cols)
			if current_page == 0:
				display_page = 1
			print '\nDisplaying page {} of {}'.format(display_page, num_pages)
			index = get_choice(list(foo[current_page]), len(game_list), num_pages=num_pages, current_page=current_page)
			if index == 'p':
				current_page -= 1
				if current_page > 0:
					display_page = current_page + 1
				else:
					display_page = 1
			elif index == 'n':
				current_page += 1
				display_page = current_page + 1

	game_to_play = int(index) - 1
	result = game_expr.parseString(game_list[game_to_play])
	print Fore.WHITE + 'Now launching ' + Fore.MAGENTA + result['Game_Name'] + Fore.WHITE + '...'
	command = 'moonlight stream -1080 -app ' + '"' + result['Game_Name'] + '"'
	try:
		os.system(command)
	except subprocess.CalledProcessError:
		print 'Moonlight needs to be installed and in the path'
		sys.exit(-1)


if __name__ == '__main__':
	args = docopt(__doc__)
	main(args)
