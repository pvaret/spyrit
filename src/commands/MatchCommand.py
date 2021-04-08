# -*- coding: utf-8 -*-

## Copyright (c) 2007-2021 Pascal Varet <p.varet@gmail.com>
##
## This file is part of Spyrit.
##
## Spyrit is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License version 2 as published by the Free
## Software Foundation.
##
## You should have received a copy of the GNU General Public License along with
## Spyrit; if not, write to the Free Software Foundation, Inc., 51 Franklin St,
## Fifth Floor, Boston, MA  02110-1301  USA
##

##
## MatchCommand.py
##
## Commands to manage matches.
##


from Matches import MatchCreationError
from .BaseCommand import BaseCommand


class MatchCommand(BaseCommand):

    """Create, list, delete match patterns."""

    def cmd_add(self, world, pattern, group=None, type="smart"):

        """
        Add a new match pattern.

        Usage: %(cmd)s <pattern> [<group>] [type="smart"|"regex"]

        The <group> parameter lets you specify the name of a group for the match,
        so patterns with the same semantics and on which the same action must be
        taken when a match is found, can be put together.

        If the given group doesn't already exist, it will be automatically created.
        If the parameter is left unspecified, the command creates a new group using
        the next available ordinal number as its name, i.e. '1', '2', '3'...

        The <type> parameter allows you to choose the syntax for the pattern:
        'smart' or 'regex'. If unspecified, the default is 'smart'.

        'smart' is a very simple pattern syntax:
            '*' matches anything, as many characters as it can;
            '%%' matches anything, as few characters as it can;
            '[<token>]' matches anything as token <token>.
        The characters '*', '%%', '[' and ']' can be escaped with a backslash.

        'regex' follows the usual syntax of regular expressions:
            http://docs.python.org/library/re.html
        Named regular expression groups are used as the pattern's tokens.

        Tokens can be used by other commands to single out parts of the match to
        highlight or otherwise act upon.

        Don't forget to quote the pattern if it contains spaces!

        Examples:
            %(cmd)s "You have received a message from *"
            %(cmd)s "[player] pages: [message]" group=pages
            %(cmd)s "From afar, (?P<player>\w+) pages (?P<message>.+)" group=pages type=regex

        """

        mgr = world.socketpipeline.triggersmanager

        try:
            match = mgr.createMatch(pattern, type)

        except MatchCreationError as e:
            world.info("%s" % e)
            return

        mgr.findOrCreateTrigger(group).addMatch(match)
        world.info("Match added.")

    def cmd_del(self, world, group, number=None):

        """
        Delete a match pattern or group of match patterns.

        Usage: %(cmd)s <group> [<number>]

        If the match pattern number is provided, only that pattern is deleted from
        the group.  If it isn't, the whole group is deleted.

        Note that if you delete the last pattern from a group, then the group is
        deleted as well.

        Examples:
            %(cmd)s pages 3
            %(cmd)s pages

        Given a match group called 'pages' containing more than three match
        patterns, the first command deletes the third pattern in the group, and the
        second command deletes the whole group.

        """

        mgr = world.socketpipeline.triggersmanager

        if not mgr.hasGroup(group):

            world.info("No such match pattern group as '%s'!" % group)
            return

        if number is None:

            mgr.delGroup(group)
            world.info("Match pattern group '%s' deleted." % group)

        else:

            if not number.isdigit():

                world.info("Match pattern number argument must be a number!")
                return

            number = int(number)

            size = mgr.sizeOfGroup(group)

            if number > size:

                world.info(
                    "Match pattern group '%s' only has %d pattern(s)!"
                    % (group, size)
                )
                return

            if number > 0:
                number -= 1  ## Match is given as 1-index but used as 0-index.

            if size > 1:

                mgr.delMatch(group, number)
                world.info(
                    "Match pattern #%d deleted from group '%s'."
                    % (number + 1, group)
                )

            else:

                mgr.delGroup(group)
                world.info(
                    "Match pattern group '%s' is now empty and was deleted."
                    % group
                )

    def cmd_action(self, world, group, action, *args, **kwargs):

        """
        Add a match action to the provided group.

        Usage: %(cmd)s <group> <action> [<parameters...>]

        If the given action already exists in the group, it is updated instead.

        Available actions are:
          highlight - colorize the matching pattern or token
          play      - play a WAV sound file when a line matches
          gag       - don't display the matching line

        The required parameters depend on the chosen action.

        Action parameters:
          highlight <format> [token=<token>]
            <format> is a format description. It is a semicolon-separated list of
              format parameters. Possible format parameters are 'bold', 'italic',
              'underline' and 'color: #rrggbb' (without quotes). Don't forget to
              quote the format description.
            <token> is the identifier of a token defined in a match pattern. If
              this argument is omitted, the highlight applies to the whole pattern.

          play [<soundfile>]
            <soundfile> is the path to a WAV sound file. If this argument is
              omitted, a default 'pop' sound is used.

          gag
            This action takes no argument.

        Examples:
          Assuming a group 'my_pages' containing the following pattern:
            [player] pages: "[message]"

          %(cmd)s my_pages highlight "bold ; color: #ffffff"
          %(cmd)s my_pages highlight "underline" token=player

          The above makes the whole line white and bold; the name of the player who
          pages you is also underlined.

          %(cmd)s my_pages play /path/to/sound.wav

          The above plays the given sound file when you receive a page.

          %(cmd)s my_pages gag

          The above hides all the pages you receive.

        """

        mgr = world.socketpipeline.triggersmanager

        if not mgr.hasGroup(group):

            world.info("No such match pattern group as '%s'!" % group)
            return

        act, msg = mgr.loadAction(action, args, kwargs)

        if not act:
            world.info(msg)
            return

        mgr.findOrCreateTrigger(group).addAction(act)

        world.info(
            "Action '%s' added to match pattern group '%s'." % (action, group)
        )

    def cmd_delaction(self, world, group, number):

        """
        Delete an action from the given match pattern group.

        Usage: %(cmd)s <group> <number>

        Example:
          %(cmd)s my_pages 2

        Given a match pattern group 'my_pages' containing several actions, the
        above command deletes the second action from the group.

        """

        mgr = world.socketpipeline.triggersmanager

        if not mgr.hasGroup(group):

            world.info("No such match pattern group as '%s'!" % group)
            return

        if not number.isdigit():

            world.info("Match pattern number argument must be a number!")
            return

        number = int(number)

        size = len(mgr.findOrCreateTrigger(group).actions)

        if number > size:

            world.info(
                "Match pattern group '%s' only has %d action(s)!"
                % (group, size)
            )
            return

        if number > 0:
            number -= 1  ## Match is given as 1-index but used as 0-index.

        mgr.delAction(group, number)
        world.info(
            "Action #%d deleted from match group '%s'." % (number + 1, group)
        )

    def cmd_test(self, world, line):

        """
        Test an input line against every match pattern group.

        Report which group matches the line, and what tokens, if any, have been
        recognized.

        Usage: %(cmd)s <line>

        Don't forget to enclose the line in quotes.

        Example:
          Assuming a group 'my_pages' containing the following pattern:
            [player] pages: "[message]"

          %(cmd)s 'Arthur pages: "Hi!"'

          The above command reports that the group 'my_pages' matches, with the
          tokens 'player' and 'message' containing 'Arthur' and 'Hi!' respectively.

        """

        mgr = world.socketpipeline.triggersmanager

        matches = list(mgr.findMatches(line))

        if not matches:
            world.info("No match found.")
            return

        msg = []
        msg.append("Matches found:")

        for matchgroup, matchresult in matches:

            group = matchgroup.name
            tokens = sorted(
                (tok, value)
                for tok, value in matchresult.groupdict().items()
                if value is not None
            )

            if tokens:

                msg.append("Group '%s' matches with tokens:" % group)
                for token, value in tokens:
                    msg.append("  %s: %s" % (token, value))

            else:
                msg.append("Group '%s' matches." % group)

        world.info("\n".join(msg))

    def cmd_list(self, world):

        """
        List all match groups with their match patterns and related actions.

        Usage: %(cmd)s

        """

        mgr = world.socketpipeline.triggersmanager

        msg = []
        msg.append("Match patterns:")

        if mgr.isEmpty():
            msg.append("  None.")

        for key, matchgroup in sorted(mgr.groups.items()):

            group = matchgroup.name

            msg.append("[%s]" % group)

            for i, m in enumerate(matchgroup.matches):

                if i == 0:
                    msg.append("  Patterns:")

                msg.append("    #%d: " % (i + 1) + m.toString())

            for i, a in enumerate(matchgroup.actions.values()):

                if i == 0:
                    msg.append("  Actions:")

                msg.append("    #%d: " % (i + 1) + a.toString())

        world.info("\n".join(msg))
