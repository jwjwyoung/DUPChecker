import os
import sys

option = sys.argv[1]
app_folders = ["../hadoop", "../hbase", "../cassandra"]
for app in app_folders:
    app_name = app.split("/")[-1]
    cmd = "python3 traverse_files.py --app=\"{}\" {} > log/{}_total.log".format(app, option, app_name)
    print(cmd)
    os.system(cmd)
