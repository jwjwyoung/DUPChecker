import os

app_folders = ["../cassandra", "../hbase", "../hadoop"]
for app in app_folders:
    cmd = "python traverse_files.py --app={} --excep".format(app)
    os.system(cmd)
