#!/usr/bin/env python

#pass in directory root file,it will loop through all files within directory and export json file 

import os
import errno

def path_hierarchy(path):
    hierarchy = {
        'type': 'folder',
        'name': os.path.basename(path),
        'path': path,
    }

    try:
        hierarchy['children'] = [
            path_hierarchy(os.path.join(path, contents))
            for contents in os.listdir(path)
        ]
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        hierarchy['type'] = 'file'

    return hierarchy



    



    

if __name__ == '__main__':
    import json
    import sys

    try:
        directory = sys.argv[1]
    except IndexError:
        directory = r"C:\Users\juzou\Desktop\General"
    
    with open(r'dhub\reference_data\constant\data.json', 'w', encoding='utf-8') as f:
        json.dump(path_hierarchy(directory), f, ensure_ascii=False, indent=4)
        #json.dump(path_hierarchy(directory, f, ensure_ascii=False, indent=4)
        #json.dump(json.dumps(path_hierarchy(directory)),f)
        #print(json.dumps(path_hierarchy(directory), indent=2, sort_keys=True).replace("u\'","\'"))
    
        #print(json.dumps(path_hierarchy(directory), indent=2, sort_keys=True).replace("u\'","\'"))