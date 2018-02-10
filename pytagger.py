import sys

import tagger

del sys.argv[0]


def display_usage (kwargs):
    print (tagger.help_text)


def set_verbose (kwargs):
    kwargs.update ({'verbose': True})


def clear_old (kwargs):
    kwargs.update ({'clear_old': True})


tag_options = [opt[0] for opt in tagger.tag_list]
tag_long_options = [opt[1] for opt in tagger.tag_list]
tag_dict = {opt[0]: opt[1] for opt in tagger.tag_list}

cmd_list = [
    ('h', 'help', display_usage),
    ('v', 'verbose', set_verbose),
    ('c', 'clear-old', clear_old)
]

cmd_options = [opt[0] for opt in cmd_list]
cmd_long_options = [opt[1] for opt in cmd_list]
cmd_dict = {opt[0]: opt[1] for opt in cmd_list}
cmd_actions = {opt[1]: opt[2] for opt in cmd_list}

active_tag = None
args = []
option_kwargs = {}
kwargs = {opt[1]: [] for opt in tagger.tag_list}

for arg in sys.argv:
    if arg.startswith ('--'):
        try:
            opt, value = arg.replace ('--', '', 1).split ('=', 1)
            try:
                kwargs[opt].append (value)
            except KeyError:
                raise tagger.UnknownOptionError (opt)
        except ValueError:
            opt = arg.replace ('--', '', 1)
            try:
                cmd_actions[opt] (option_kwargs)
            except KeyError:
                raise tagger.UnknownOptionError (opt)
    elif arg.startswith ('-'):
        opt = arg.replace ('-', '', 1)
        try:
            cmd_actions[cmd_dict[opt]] (option_kwargs)
        except KeyError:
            if opt in tag_options:
                active_tag = tag_dict[opt]
            else:
                raise tagger.UnknownOptionError (opt)
    elif active_tag:
        kwargs[active_tag] = arg
        active_tag = None
    else:
        args.append (arg)

real_kwargs = kwargs.copy ()

for k in kwargs:
    if not kwargs[k]:
        del real_kwargs[k]

for filename in args:
    tager = tagger.Tagger (filename, **real_kwargs)
    tager.apply ()
