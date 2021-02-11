import json
import sys
import os
import csv
import argparse
import copy


NEWLINE="\n"

SKIP_COLUMN_KEYS=["age", "since", "lastheartbeattime", "lasttransitiontime", "time", "resourceVersion", "generation"]

def BFS(top_dict, looking_for_key):
    # queue
    dict_q = [top_dict] # list of dictionaries
    # magic math
    for d in dict_q:
        dict_keys = d.keys()
        for k in dict_keys:
            if k == looking_for_key:
                return d[k] 
            if isinstance(d[k], dict):
                dict_q.append(d[k]) 

def check_ignore(ignore_dict, element_dictionary):
    for key in ignore_dict.keys():
        if BFS(element_dictionary, key) in ignore_dict[key]:
            return True
    return False

def read_file_as_dict(file_path):
    _resource_info_dict = dict()
    _details_file=file_path
    _read_file = open(_details_file, 'r') 
    while True:
        _resource_type=_read_file.readline().strip()
        if not _resource_type:
            break
        _resource_details_json=_read_file.readline()
        _resource_details_dict=json.loads(_resource_details_json)
        if _resource_details_dict:
            _resource_info_dict[_resource_type]=_resource_details_dict
    _read_file.close ()

    return _resource_info_dict

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
        if k.lower() in map(str.lower, SKIP_COLUMN_KEYS):
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

def diffTheLists(list_one, list_two):

    results = {
        "both": [],
        "added": [],
        "removed": []
    }

    # gotta check both directions
    for n in list_one:
        if n in list_two:
            results["both"].append(n)
        else:
            results["removed"].append(n)
    
    for n in list_two:
        if n not in list_one:
            results["added"].append(n)

    return results

def spotTheDifference(json_dict_one,  json_dict_two):
    results = {
        "both": dict(),
        "added": dict(),
        "removed": dict()
    }
    _resource_list_one=json_dict_one.keys()
    _resource_list_two=json_dict_two.keys()
    _resource_diffs  = diffTheLists(_resource_list_one, _resource_list_two)
    for a in _resource_diffs["added"]:
        if len(json_dict_two[a]) > 0: 
            results["added"][a] = json_dict_two[a]
    for r in _resource_diffs["removed"]:
        results["removed"][r] = json_dict_one[r]
    for b in _resource_diffs["both"]:
        _row_diffs = diffTheLists(json_dict_one[b], json_dict_two[b])
        for a in _row_diffs["added"]:
            if b not in results["added"]:
                results["added"][b] = []
            results["added"][b].append(a)
        for r in _row_diffs["removed"]:
            if b not in results["removed"]:
                results["removed"][b] = []
            results["removed"][b].append(r)
        for bo in _row_diffs["both"]:
            if b not in results["both"]:
                results["both"][b] = []
            results["both"][b].append(bo)
    return results

def removeIgnoredItems(res_dict, ignore_dict):
    # add support for removing kind
    if "kind" in ignore_dict.keys():
        remove_kinds = ignore_dict["kind"]
        for kind in remove_kinds:
            res_dict.pop(kind, None)

    for k in res_dict.keys():
        res_dict[k][:] = [item for item in res_dict[k] if not check_ignore(ignore_dict, item)]                       
    return res_dict

def removeEmptyResults(res_dict):
    copy_dict=copy.deepcopy(res_dict)
    dict_keys = copy_dict.keys()
    for k in dict_keys:
        if type(copy_dict[k]) is list and not copy_dict[k]: #empty list
            del res_dict[k]
    return res_dict
    
def writeJSON(file_path, res_dict):
    _file = open(file_path, "w")
    _file.write(json.dumps(res_dict, indent=2))
    _file.close()

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--first_file", required=True)
    parser.add_argument("-s", "--second_file", required=True)
    parser.add_argument("-c", "--ignore_file", required=False)
    parser.add_argument("-o", "--output_tag", required=True)
    args = vars(parser.parse_args())
    _first_file_path = args['first_file']
    _second_file_path = args['second_file']
    _ignore_file_path = args['ignore_file']
    _output_tag = args['output_tag']
    _first_resource_dict_list = read_file_as_dict(_first_file_path)
    _second_resource_dict_list = read_file_as_dict(_second_file_path)
    
    # _results = spotTheDifference(_first_resource_dict_list, _second_resource_dict_list)

    _pruned_first_resource_dict_list = pruneDictOfLists(_first_resource_dict_list)
    _pruned_second_resource_dict_list = pruneDictOfLists(_second_resource_dict_list)
    _results = spotTheDifference(_pruned_first_resource_dict_list, _pruned_second_resource_dict_list)

    if _ignore_file_path:
        with open(_ignore_file_path) as f:
            _ignore_dictionary=json.load(f)
    else:
        _ignore_dictionary = {}

    _res_both = removeIgnoredItems(_results["both"], _ignore_dictionary)
    _res_added = removeIgnoredItems(_results["added"], _ignore_dictionary)
    _res_removed = removeIgnoredItems(_results["removed"], _ignore_dictionary)

    _res_both = removeEmptyResults(_res_both)
    _res_added = removeEmptyResults(_res_added)
    _res_removed = removeEmptyResults(_res_removed)

    writeJSON("./results/both-results-"+_output_tag, _res_both)
    writeJSON("./results/added-results-"+_output_tag, _res_added)
    writeJSON("./results/removed-results-"+_output_tag, _res_removed)

main()