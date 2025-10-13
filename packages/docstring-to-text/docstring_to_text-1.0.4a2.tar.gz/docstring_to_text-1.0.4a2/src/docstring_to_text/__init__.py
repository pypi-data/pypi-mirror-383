# encoding: utf-8
"""
A simple pip package converting docstrings into clean text (proper paragraphs and indents).
"""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import typing as _t

from inspect import cleandoc, getdoc
import re as _re

from .___package_meta import VERSION
from .___package_meta import VERSION as __version__

# TODO:
# - lists
#   formatted with indents
#   in all lines except for the first one
#
# Also...
#   - preserve indents
#   - of the entire list
#
# And...
#   - ensure
#     that
#     - it all works
#       with nested lists


_re_indent_match = _re.compile(r"(\t*)( +)(\t*)(.*?)$").match
_re_tab_indent_match = _re.compile(r"(\t+)(.*?)$").match
_re_list_line_match = _re.compile(
	r"(\s*)("
	r"[-*•]+"
	r"|"
	r"[a-zA-Z]\s*[.)]"
	r"|"
	r"[0-9+]\s*[.)]"
	r")\s+"
).match


def _recover_tab_indents(line: str, tab_size: int):
	"""Turn indenting spaces back to tabs using regexp. Half-tab indents are rounded."""
	assert bool(line) and isinstance(line, str)

	n_tabs = 0.0

	match = _re_indent_match(line)
	while match:
		pre_tabs, spaces, post_tabs, line = match.groups()
		n_tabs_from_spaces = float(len(spaces)) / tab_size + 0.00001
		n_post_tabs = len(post_tabs)
		if n_post_tabs > 0:
			# There are tabs after spaces. Don't preserve the fractional spaces-indent, truncate it:
			n_tabs_from_spaces = int(n_tabs_from_spaces)
		n_tabs += len(pre_tabs) + n_tabs_from_spaces + n_post_tabs
		match = _re_indent_match(line)

	if n_tabs < 0.5:
		return line

	tabs_prefix = '\t' * int(n_tabs + 0.50001)
	return f"{tabs_prefix}{line}"


def _join_paragraph_and_format_tabs(paragraph: _t.List[str], tab_size: int):
	"""
	Given "continuous" paragraph (i.e., with no empty newlines between chunks), recover tabs for each chunk
	and join them together into a single actual line.
	Works as a generator to account for blocks with different indents - to make each its own line.
	"""
	pending_indent = 0
	pending_chunks: _t.List[str] = list()

	def join_pending_chunks() -> str:
		return "{}{}".format('\t' * pending_indent, ' '.join(pending_chunks))

	for chunk in paragraph:
		chunk = _recover_tab_indents(chunk, tab_size)

		cur_indent = 0
		match = _re_tab_indent_match(chunk)
		if match:
			tab_indent, chunk = match.groups()  # We've detected indent. Now, get rid of it.
			cur_indent = len(tab_indent)

		match_list_line = _re_list_line_match(chunk)
		# In case of a bulleted/numbered list, we'll need to start a new block, too.
		if cur_indent == pending_indent and not match_list_line:
			pending_chunks.append(chunk)
			continue

		# Indent mismatch or a list line:
		# we're either ended one block or entered another. Either way, the previous block ends.
		if pending_chunks:
			yield join_pending_chunks()
			pending_chunks = list()
		assert not pending_chunks
		pending_chunks.append(chunk)
		pending_indent = cur_indent

	if pending_chunks:
		yield join_pending_chunks()


def _formatted_paragraphs_gen(doc: str, tab_size: int):
	"""
	Generator, which splits docstring into lines and transforms them into an actual printable output:
	- From each bulk of empty lines, the first one is skipped...
	- ... thus, non-empty lines are joined into continuous paragraphs.
	- Recover tabs in the beginning oh lines (``inspect.cleandoc()`` converts them into spaces).
	"""
	if not doc:
		return
	doc = str(doc)
	if not doc.strip():
		return

	tab_size = max(int(tab_size), 1)

	cur_paragraph: _t.List[str] = list()

	for line in doc.splitlines():
		line: str = line.rstrip()
		if line:
			cur_paragraph.append(line)
			continue

		assert not line
		if cur_paragraph:
			for block in _join_paragraph_and_format_tabs(cur_paragraph, tab_size):
				yield block
			cur_paragraph = list()
			# Just skip the current empty line entirely - do nothing with it.
			continue

		# We're in a chain of empty lines, and we've already skipped the first one. Preserve the remaining ones:
		yield ''

	# Return the last paragraph post-loop:
	if cur_paragraph:
		for block in _join_paragraph_and_format_tabs(cur_paragraph, tab_size):
			yield block


def format_docstring(doc: str, tab_size: int = 8) -> str:
	"""
	Turn a pre-cleaned-up docstring (with tabs as spaces and newlines mid-sentence)
	into an actually printable output:
	- mid-paragraph new lines are replaced with spaces...
	- ... while still keeping indented blocks separate.

	Remember to pass a pre-cleaned-up docstring - i.e., with one of:
	- format_docstring(inspect.cleandoc(__doc__))
	- format_docstring(inspect.getdoc(class_or_function))
	"""
	return '\n'.join(_formatted_paragraphs_gen(doc, tab_size))


def format_object_docstring(_obj, tab_size: int = 8) -> str:
	"""Find the object's docstring and format it with ``format_docstring()``"""
	doc = getdoc(_obj)
	if not doc:
		return ''
	# noinspection PyArgumentList
	return format_docstring(doc, tab_size=tab_size)
