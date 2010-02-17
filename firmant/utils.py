# Copyright (c) 2010, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Firmant nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def get_module(plugin):
    '''Retrieve a module by named path.

        >>> # Returns a module object on success.
        >>> get_module('testdata.settings.full') #doctest: +ELLIPSIS
        <module 'testdata.settings.full' from '...testdata/settings/full.pyc'>

        >>> # An ImportError is raised on non-existant settings.
        >>> get_module('testdata.settings.noexist')
        Traceback (most recent call last):
        ImportError: No module named noexist


    '''
    try:
        modules = plugin.split('.')
        mod = __import__(plugin, {}, {}, [])
        for module in modules[1:]:
            mod = getattr(mod, module)
        return mod
    except ImportError:
        raise


def mod_to_dict(module):
    '''Convert a module object to a dictionary.

    All uppercase names within the module will be placed into a dictionary.

        >>> from pprint import pprint
        >>> pprint(mod_to_dict(get_module('testdata.settings.empty')))
        {}

        >>> from pprint import pprint
        >>> pprint(mod_to_dict(get_module('testdata.settings.full')))
        {'DICT_TEST': {"g'bye": 'world', 'hello': 'world'},
         'INT': 42,
         'LIST_TEST': [1, 2, 3, 4, 5],
         'SET_TEST': set([1, 2, 3, 4, 5]),
         'SINGLE_TUPLE_TEST': (1,),
         'STRING': 'hello world',
         'TUPLE_TEST': (1, 2, 3, 4, 5)}

    '''
    dictionary = dict()
    for attr in dir(module):
        if attr.upper() == attr:
            value = getattr(module, attr)
            dictionary[attr] = value
    return dictionary
