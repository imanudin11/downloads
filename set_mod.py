"""Set a member or members moderated flag.

Save as bin/set_mod.py

Run via

   bin/withlist -r set_mod <listname> <option> <member> ...

Option:
    -s
    --set
        Set moderation on for listed member(s)
    -u
    --unset
        Set moderation off for listed member(s)
    -d pattern
    --domain=pattern
        Process all members with addresses that match the regexp 'pattern'
    -a
    --all
        Process all members

Member addresses can be repeated as necessary. The -d/--domain option may be
specified with or without additional member addresses, but these may not be
specified in conjunction with -a/--all. For example, to set moderation on for
user1@example.com and all users in the example.net domain or a subdomain
thereof, you could use the command

   bin/withlist -r set_mod --set --domain='[@.]example\.net$' user1@example.com

Note the use of single quotes to prevent the shell from assigning special
meaning to characters like [, \ and $.
"""

import re
import sys
import getopt

from Mailman import mm_cfg

def usage(code, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__
    if msg:
        print >> fd, msg
    sys.exit(code)

def set_mod(mlist, *args):

    try:
        opts, args = getopt.getopt(args, 'sud:a',
                                   ['set', 'unset', 'domain=', 'all'])
    except getopt.error, msg:
        usage(1, msg)

    action = None
    domain = None
    all = None
    for opt, arg in opts:
        if opt in ('-s', '--set'):
            if action in (0, 1):
                usage(1, 'Exactly one of -s, --set, -u, --unset required')
            action = 1
        if opt in ('-u', '--unset'):
            if action in (0, 1):
                usage(1, 'Exactly one of -s, --set, -u, --unset required')
            action = 0
        if opt in ('-d', '--domain'):
            if domain:
                usage(1, 'Only one -d/--domain can be specified')
            domain = re.compile(arg, re.I)
        if opt in ('-a', '--all'):
            all = 1
    if action == None:
        usage(1, 'Exactly one of -s, --set, -u, --unset required')
    if not args and not domain and not all:
        usage(1, 'Member address(es), -d/--domain or -a/--all is required')
    if (args or domain) and all:
        usage(1, 'Do not specify -a/--all and member address(es)/domain')
    if all:
        args = mlist.getMembers()
    if domain:
        args = list(args) + [x for x in mlist.getMembers()
                             if domain.search(x)]

    if not mlist.Locked():
        mlist.Lock()
    for member in args:
        mlist.setMemberOption(member, mm_cfg.Moderate, action)
    mlist.Save()
    mlist.Unlock()
