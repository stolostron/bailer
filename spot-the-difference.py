import sys
import os
 
COMMAND_SEPARATOR="---\n"
NEWLINE="\n"
COMMAND_PREFIX=">"
SKIP_COLUMN_KEYS=["age"]
STRING_JOINER="   "

def envVarsReady():
    if not "FIRST_FILE" in os.environ:
        print("ERROR: MUST EXPORT FIRST FILE PATH AS `FIRST_FILE`")
        return False
    if not "SECOND_FILE" in os.environ:
        print("ERROR: MUST EXPORT SECOND FILE PATH AS `SECOND_FILE`")
        return False
    # NW add env vars for result files
    return True

# this will save spaces in command row where spaces need saved
def splitCommandRow(row):
    _split_row = row.strip().split("  ") # two spaces to protect column keys with space in them
    _split_row[:] = [x.strip() for x in  _split_row if x.strip()]
    return _split_row

class CommandInfo:
    def __init__(self, command_chunk):
        _full_command_as_array = command_chunk.split(NEWLINE)
        _just_command_string = _full_command_as_array.pop(0)
        if not _full_command_as_array:
            self.command = _just_command_string.replace(COMMAND_PREFIX, "").strip() # without "> "
            self.column_keys = []
            self.resource_rows = []
            self.resource_rows_as_strings = []
            return
        _just_column_keys = _full_command_as_array.pop(0)

        _rows = []

        for _row in _full_command_as_array:
            _rows.append(splitCommandRow(_row))

        self.command = _just_command_string.replace(COMMAND_PREFIX, "").strip() # without "> "
        self.column_keys = splitCommandRow(_just_column_keys)
        self.resource_rows = _rows
        self.resource_rows_as_strings = self.makeResourceRowsIntoListOfStrings()
    
    def makeResourceRowsIntoListOfStrings(self):
        _column_keys = self.getColumnKeys()
        _resource_rows = self.getResourceRows()
        _resource_rows_as_strings = [] 
        for r in _resource_rows:
            _row_string = ""
            for _ind, _val in enumerate(r):
                _curr_column_key = _column_keys[_ind]
                if _curr_column_key.lower() in map(str.lower, SKIP_COLUMN_KEYS):
                    continue
                else:
                    _row_string += (STRING_JOINER + _val)
            _resource_rows_as_strings.append(_row_string.strip())
        return _resource_rows_as_strings

    def getResource(self):
        return self.command.split()[2]

    def getCommand(self):
        return self.command

    def getColumnKeys(self):
        return self.column_keys
    
    def getResourceRows(self):
        return self.resource_rows
    
    def getResourceRowsAsStrings(self):
        return self.resource_rows_as_strings

"""
    command_chunk is the ENTIRE string, from "> oc get ..." to the last newline of the last result
    If no resource of that kind found, _full_command_as_array will be len == 1
"""

def readFileAsCommandInfoDict(file_path):
    _command_info_dict = dict()
    try:
        _file = open(file_path, "r")
        _file_as_string = _file.read()
    except:
        print("ERROR: Something's wrong with file path {}".format(file_path))
        return
    _command_chunks  = _file_as_string.strip().split(COMMAND_SEPARATOR)
    _command_list = []
    
    for _chunk in _command_chunks:
        if not _chunk.strip():
            continue
        _command_info = CommandInfo(_chunk.strip())
        _command_info_dict[_command_info.getResource()] = _command_info
    return _command_info_dict

def writeStringToFile(file_path, file_as_string):
    _file = open(file_path, "w")
    _file.write(file_as_string)
    _file.close()

# lists contain straight up strings
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

def spotTheDifference(command_info_dict_one,  command_info_dict_two):
    results = {
        "both": dict(),
        "added": dict(),
        "removed": dict()
    }
    _resource_list_one=command_info_dict_one.keys()
    _resource_list_two=command_info_dict_two.keys()

    _resource_diffs  = diffTheLists(_resource_list_one, _resource_list_two)
    for a in _resource_diffs["added"]:
        if len(command_info_dict_two[a].getResourceRows()) > 0: # else, recorded with CRD addition
            results["added"][a] = command_info_dict_two[a].getResourceRowsAsStrings()
    for r in _resource_diffs["removed"]:
        results["removed"][r] = command_info_dict_one[r].getResourceRowsAsStrings()
    for b in _resource_diffs["both"]:
        _resource_rows_strings_from_dict_one = command_info_dict_one[b].getResourceRowsAsStrings()
        _resource_rows_strings_from_dict_two = command_info_dict_two[b].getResourceRowsAsStrings()
        _row_diffs = diffTheLists(_resource_rows_strings_from_dict_one, _resource_rows_strings_from_dict_two)
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
        _res_string += (COMMAND_SEPARATOR) 
        _res_string += (k.upper() + NEWLINE + NEWLINE)
        for r in res_dict[k]:
            _res_string += ( r + NEWLINE )
        _res_string += NEWLINE
    return _res_string

def main():
    if not envVarsReady():
        print ("BAD BAD")
        return
    print ("GOOD TO GO")
    _first_file_path = os.environ["FIRST_FILE"]
    _second_file_path = os.environ["SECOND_FILE"]

    _first_command_info_list = readFileAsCommandInfoDict(_first_file_path)
    _second_command_info_list = readFileAsCommandInfoDict(_second_file_path)

    _res = spotTheDifference(_first_command_info_list, _second_command_info_list)

    _res_both = makeStringFromResults(_res["both"])
    _res_added = makeStringFromResults(_res["added"])
    _res_removed = makeStringFromResults(_res["removed"])

    writeStringToFile("./both-results", _res_both)
    writeStringToFile("./added-results", _res_added)
    writeStringToFile("./removed-results", _res_removed)
   


main()
