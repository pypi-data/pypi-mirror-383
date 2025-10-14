# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
import codecs
import json
import os.path
from collections import OrderedDict
from typing import MutableMapping


class SimpleJSONMappedDict(MutableMapping):
    __slots__ = ('json_file_path', 'ordered_dict')

    def __init__(self, json_file_path):
        if os.path.exists(json_file_path):
            with codecs.open(json_file_path, 'r', encoding='utf-8') as json_file:
                contents = json_file.read()
                loaded = json.loads(contents, object_pairs_hook=OrderedDict)

                if not isinstance(loaded, OrderedDict):
                    raise ValueError('JSON file %s does not contain a JSON object.' % json_file_path)
        else:
            loaded = OrderedDict()
            contents = json.dumps(loaded)

            with codecs.open(json_file_path, 'w', encoding='utf-8') as json_file:
                json_file.write(contents)

        self.json_file_path = json_file_path
        self.ordered_dict = loaded

    # Mandatory non-mutating methods
    def __contains__(self, key):
        return key in self.ordered_dict

    def __getitem__(self, key):
        return self.ordered_dict[key]

    def __iter__(self):
        return iter(self.ordered_dict)

    def __len__(self):
        return len(self.ordered_dict)

    # Optional non-mutating methods
    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.json_file_path)

    def keys(self):
        return self.ordered_dict.keys()

    def values(self):
        return self.ordered_dict.values()

    def items(self):
        return self.ordered_dict.items()

    # Mandatory mutating methods
    def __delitem__(self, key):
        del self.ordered_dict[key]

        dumps = json.dumps(self.ordered_dict)
        with codecs.open(self.json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(dumps)

    def __setitem__(self, key, value):
        if key in self.ordered_dict:
            displaced_value = self.ordered_dict[key]
            self.ordered_dict[key] = value
            try:
                # test-serialization
                dumps = json.dumps(self.ordered_dict)
            except:
                # if serialization fails, roll back the in-memory state
                self.ordered_dict[key] = displaced_value
                raise
        else:
            self.ordered_dict[key] = value
            try:
                # test-serialization
                dumps = json.dumps(self.ordered_dict)
            except:
                # if serialization fails, roll back the in-memory state
                del self.ordered_dict[key]
                raise

        # write if it succeeds
        with codecs.open(self.json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(dumps)

    # Optional mutating methods
    def clear(self):
        self.ordered_dict.clear()

        dumps = json.dumps(self.ordered_dict)
        with codecs.open(self.json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(dumps)

    def update(self, other=(), **kwargs):
        backup = self.ordered_dict.copy()
        self.ordered_dict.update(other, **kwargs)
        try:
            # test-serialization
            dumps = json.dumps(self.ordered_dict)
        except:
            # if serialization fails, roll back the in-memory state
            self.ordered_dict.clear()
            self.ordered_dict.update(backup)
            raise

        # write if it succeeds
        with codecs.open(self.json_file_path, 'w', encoding='utf-8') as json_file:
            json_file.write(dumps)
