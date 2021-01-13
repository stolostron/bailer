import json
import sys
import os

NEWLINE="\n"

def read_file_as_dict(file_path):
    _resource_info_dict = dict()
    _details_file=file_path
    _read_file = open(_details_file, 'r') 
    while True:
        _resource_type=_read_file.readline().strip()
        print(_resource_type)
        if not _resource_type:
            break
        _resource_details_json=_read_file.readline()
        _resource_details_dict=json.loads(_resource_details_json)
        if _resource_details_dict:
            _resource_info_dict[_resource_type]=_resource_details_dict
    _read_file.close ()

    return _resource_info_dict

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

def makeStringFromResults(res_dict):
    _res_string = ""
    for k in res_dict.keys():
        _res_string += (k + NEWLINE + NEWLINE)
        for r in res_dict[k]:
            _res_string += ( json.dumps(r) + NEWLINE )
        _res_string += NEWLINE
    return _res_string 
def writeStringToFile(file_path, file_as_string):
    _file = open(file_path, "w")
    _file.write(file_as_string)
    _file.close()

def main():
    _first_file_path = os.environ["FIRST_FILE"]    
    _second_file_path = os.environ["SECOND_FILE"]
    _first_resource_dict_list = read_file_as_dict(_first_file_path)
    _second_resource_dict_list = read_file_as_dict(_second_file_path)
    _results = spotTheDifference(_first_resource_dict_list, _second_resource_dict_list)
    _res_both = makeStringFromResults(_results["both"])
    _res_added = makeStringFromResults(_results["added"])
    _res_removed = makeStringFromResults(_results["removed"])

    writeStringToFile("./both-results-cam", _res_both)
    writeStringToFile("./added-results-cam", _res_added)
    writeStringToFile("./removed-results-cam", _res_removed)


main()