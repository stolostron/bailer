import copy

SKIP_COLUMN_KEYS=["age", "since"]

thisdict = {
  "brand": [
    {
      "soda": "coke"
    },
    {
      "cars": {
        "truck": [
          "chevy",
          "ford",
          "dodge"
        ],
        "sport": [
          "mustang",
          "corvette"
        ],
        "scooter": "vespa"
      }
    },
    {
      "kitchenstuff": [
        "instapot",
        "crockpot",
        "kitchenaid"
      ]
    },
    {
      "other": "stuff",
      "age": "young"
    }
  ],
  "model": [
    {
      "train": [
        "small",
        "big"
      ]
    },
    {
      "plane": "zooom"
    },
    {
      "americas next top": [
        "chef",
        "baker",
        {
          "model": {
            "since": "stuff",
            "age": "ancient"
          }
        }
      ]
    }
  ],
  "year": [
    {
      "abc": "of the cat"
    },
    {
      "def": "of the tiger"
    },
    {
      "fake": "stuff",
      "age": "old"
    }
  ],
  "listof": [
    {
      "innerlist": [
        "lists",
        "things",
        "bat",
        "age",
        {
          "cow": "moo",
          "since": [
            "abc",
            "def"
          ],
          "age": {
            "foo": "bar"
          }
        }
      ]
    }
  ]
}

def pruneList(l):
    for i in range(len(l)):
        item = l[i]
        if type(item) is list:
            l[i] = pruneList(item)
        elif type(item) is dict:
            l[i] = pruneDict(item)
        # else skip
    return l

def pruneDict(d):
    dict_copy = copy.deepcopy(d)
    dict_keys = dict_copy.keys()
    for k in dict_keys:
        if k in SKIP_COLUMN_KEYS:
            del d[k]
            continue
        value_from_key = d[k]
        if type(value_from_key) is list:
            d[k] = pruneList(value_from_key)
        elif type(value_from_key) is dict:
            d[k] = pruneDict(value_from_key)
        # else skip
    return d

def pruneDictOfLists(dict_of_lists):
    dict_keys = dict_of_lists.keys()
    for k in dict_keys:
        l_o_t = dict_of_lists[k]
        dict_of_lists[k] = pruneList(l_o_t)
    return dict_of_lists


print ("BEFORE")
print (thisdict)
print()
thisdict = pruneDictOfLists(thisdict)
print()
print ("AFTER")
print(thisdict)
print()



# if type(item) is list:
#             print ("item is a list " + str(item))
#         elif type(item) is dict:
#             print ("item is a dict " + str(item))
#         else:
#             print ("<"+item + "> not an obj, of type {}".format(str(type(i))))