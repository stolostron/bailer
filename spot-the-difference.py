import sys
import os
 
COMMAND_SEPARATOR="---\n"
COMMAND_PREFIX=">"

def envVarsReady():
    if not "FIRST_FILE" in os.environ:
        print("ERROR: MUST EXPORT FIRST FILE PATH AS `FIRST_FILE`")
        return False
    if not "SECOND_FILE" in os.environ:
        print("ERROR: MUST EXPORT SECOND FILE PATH AS `SECOND_FILE`")
        return False
    return True

# this will save spaces in command row where spaces need saved
def splitCommandRow(row):
    _split_row = row.strip().split("  ") # two spaces to protect column keys with space in them
    _split_row[:] = [x.strip() for x in  _split_row if x.strip()]
    return _split_row

class CommandInfo:
    def __init__(self, command_chunk):
        _full_command_as_array = command_chunk.split("\n")
        _just_command_string = _full_command_as_array.pop(0)
        if not _full_command_as_array:
            self.command = _just_command_string.replace(COMMAND_PREFIX, "").strip() # without "> "
            self.column_keys = []
            self.rows = []
            return
        _just_column_keys = _full_command_as_array.pop(0)

        _rows = []

        for _row in _full_command_as_array:
            _rows.append(splitCommandRow(_row))

        self.command = _just_command_string.replace(COMMAND_PREFIX, "").strip() # without "> "
        self.column_keys = splitCommandRow(_just_column_keys)
        self.rows = _rows

    def getCommand(self):
        return self.command

    def getColumnKeys(self):
        return self.column_keys
    
    def getRows(self):
        return self.rows


"""
    command_chunk is the ENTIRE string, from "> oc get ..." to the last newline of the last result
    If no resource of that kind found, _full_command_as_array will be len == 1
"""

def readFileAsCommandInfoList(file_path):
    _file_as_dict = dict()
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
        _command_list.append(_command_info)
    return _command_list

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

def spotTheDifference(command_info_list_one,  command_info_list_two):
    results = {
        "both": [],
        "added": [],
        "removed": []
    }
    print (len(command_info_list_one))
    print (len(command_info_list_two))
    list_one_commands = list(map(CommandInfo.getCommand, command_info_list_one))
    list_two_commands = list(map(CommandInfo.getCommand, command_info_list_two))
    command_diffs  = diffTheLists(list_one_commands, list_two_commands)
    print ("both: {}".format(str(len(command_diffs["both"]))))
    print ("removed: {}".format(str(len(command_diffs["removed"]))))
    print ("added: {}".format(str(len(command_diffs["added"]))))

def main():
    if not envVarsReady():
        print ("BAD BAD")
        return
    print ("GOOD TO GO")
    _first_file_path = os.environ["FIRST_FILE"]
    _second_file_path = os.environ["SECOND_FILE"]

    _first_command_info_list = readFileAsCommandInfoList(_first_file_path)
    _second_command_info_list = readFileAsCommandInfoList(_second_file_path)

    spotTheDifference(_first_command_info_list, _second_command_info_list)
   


main()
