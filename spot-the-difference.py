import json
import os
import argparse
import copy


NEWLINE="\n"

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
    return ""

def find_key_with_value (key, value, element_dictionary):
    return BFS(element_dictionary, key) == value

def get_ignore_list_file_path():
    return os.path.join(os.getcwd(), "config", "ignore.json")

def get_acm_leaks_list_file_path():
    return os.path.join(os.getcwd(), "config", "acm-leaks.json")

def read_json_file(file_path):
    if file_path:
        with open(file_path) as f:
            return json.load(f)

def read_scan_file_as_dict(file_path):
    _resource_info_dict = dict()
    _details_file=file_path
    _read_file = open(_details_file, 'r') 
    while True:
        # _resource_type=_read_file.readline().strip()
        # if not _resource_type:
        #     break
        _resource_details_json=_read_file.readline().strip()
        if not _resource_details_json:
            break
        _resource_details_dict=json.loads(_resource_details_json)
        if _resource_details_dict:
            _resource_info_dict.update(_resource_details_dict)
            # _resource_info_dict[_resource_type]=_resource_details_dict
    _read_file.close ()
    return _resource_info_dict

def simplify_dict_list(dict_of_lists):
    _attributes_we_care_about = ["kind", "name", "namespace", "pod-template-hash"]
    _dict_keys=dict_of_lists.keys()
    _simplified_dict_list = dict()
    for k in _dict_keys:
        _simplified_dict_list[k] = []
        _resource_list = dict_of_lists[k]
        for r in _resource_list: # r is a dict for a particular resource
            _simplified_resource = dict()
            for a in _attributes_we_care_about:
                _simplified_resource[a] = BFS(r, a)
            _simplified_dict_list[k].append(_simplified_resource)
    return _simplified_dict_list

def fix_name (dict_of_lists):
    _short_name_dict = dict()
    _dict_keys=dict_of_lists.keys()
    for k in _dict_keys:
        _short_name_dict[k] = []
        _resource_list = dict_of_lists[k]
        for r in _resource_list: # r is a dict for a particular resource
            _short_name_resource = dict()
            _short_name_resource["kind"] = r["kind"]
            if r["pod-template-hash"] != "":
                _short_name_resource["name"] = r["name"].split(r["pod-template-hash"])[0]
            else:
                _short_name_resource["name"] = r["name"]
            _short_name_resource["namespace"] = r["namespace"]
            _short_name_dict[k].append(_short_name_resource)
    return _short_name_dict
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


# this returns a (sub) set of the list_of_resources, having removed remove_resource
def usefulFunctNoGoodName(list_of_resources, remove_resource):
    # list_of_resources_copy = copy.deepcopy(list_of_resources)
    list_of_resources_subset = []
    for r in list_of_resources:
        remove_resource_keys = remove_resource.keys()
        should_be_kept = False
        for key in remove_resource_keys:
            if not find_key_with_value(key, remove_resource[key], r): 
                should_be_kept = True
                break
        if should_be_kept:
            list_of_resources_subset.append(r)
    return list_of_resources_subset


def removeIgnoredItems(res_dict, ignore_list):

    if len(ignore_list) == 0:
        return res_dict

    ignore_list_copy = copy.deepcopy(ignore_list)

    for remove_resource in ignore_list_copy:
        if "kind" in remove_resource.keys(): #if kind specified
            resource_kind = remove_resource["kind"]
            if resource_kind in res_dict.keys() and len(remove_resource.keys()) == 1: # if the entire kind should be removed (and that kind exists)
                res_dict.pop(resource_kind, None)
                continue
            # else, don't remove _entire_ kind
            remove_resource.pop("kind", None) # don't check kind anymore

            if resource_kind in res_dict.keys() and res_dict[resource_kind]: # if kind even exists in file
                res_dict[resource_kind] = usefulFunctNoGoodName(res_dict[resource_kind], remove_resource)
        else: # kind not specified, gotta loop through each kind
            for resource_kind in res_dict.keys():
                if res_dict[resource_kind]:
                    res_dict[resource_kind] = usefulFunctNoGoodName(res_dict[resource_kind], remove_resource)     

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

def countTotals(res_dict):
    typeCount = 0
    totalCount = 0
    for x in res_dict: 
        typeCount += 1
        totalCount += len(res_dict[x])
    return typeCount, totalCount

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--first_file", required=True)
    parser.add_argument("-s", "--second_file", required=True)
    parser.add_argument("-o", "--output_tag", required=True)
    args = vars(parser.parse_args())
    _first_file_path = args['first_file']
    _second_file_path = args['second_file']
    _output_tag = args['output_tag']

    _first_resource_dict_list = read_scan_file_as_dict(_first_file_path)
    _second_resource_dict_list = read_scan_file_as_dict(_second_file_path)

    _first_resource_dict_list_simplified = simplify_dict_list(_first_resource_dict_list)
    _second_resource_dict_list_simplified = simplify_dict_list(_second_resource_dict_list)

    _first_resource_dict_list_namefixed = fix_name(_first_resource_dict_list_simplified)
    _second_resource_dict_list_namefixed = fix_name(_second_resource_dict_list_simplified)
    
    _results = spotTheDifference(_first_resource_dict_list_namefixed, _second_resource_dict_list_namefixed)

    _res_both = _results["both"]
    _res_added = _results["added"]
    _res_removed = _results["removed"]

    _ignore_list = read_json_file(get_ignore_list_file_path())
    _acm_leaks_list = read_json_file(get_acm_leaks_list_file_path())

    _all_ignores_list = _ignore_list + _acm_leaks_list

    _res_both = removeIgnoredItems(_res_both, _all_ignores_list)
    _res_added = removeIgnoredItems(_res_added, _all_ignores_list)
    _res_removed = removeIgnoredItems(_res_removed, _all_ignores_list)

    _res_both = removeEmptyResults(_results["both"])
    _res_added = removeEmptyResults(_results["added"])
    _res_removed = removeEmptyResults(_results["removed"])

    typeCount, totalCount = countTotals(_res_added)
    with open('./results/count.txt', 'w') as f:
        f.write('Total Leak Count: '+str(totalCount))
        f.write('\n')
        f.write('Leaked Resource Kinds: '+str(typeCount))
        f.write('\n')

    # writeJSON("./results/both-results-"+_output_tag+".json", _res_both)
    # writeJSON("./results/removed-results-"+_output_tag+".json", _res_removed)
    writeJSON("./results/leaks-"+_output_tag+".json", _res_added)

main()