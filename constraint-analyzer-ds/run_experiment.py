import itertools
import os
import sys
tags_dict = {
  'hbase' :['rel/1.4.13', 'rel/1.6.0', 'rel/2.2.6', 'rel/2.3.3','master'],
  'hive' :['rel/release-1.2.2', 'rel/release-2.1.0', 'rel/release-2.1.1', 'rel/release-2.2.0', 'rel/release-2.3.0', 'rel/release-2.3.1', 'rel/release-2.3.2', 'rel/release-2.3.3', 'rel/release-2.3.4', 'rel/release-2.3.5', 'rel/release-2.3.6', 'rel/release-2.3.7', 'rel/release-3.0.0', 'rel/release-3.1.0', 'rel/release-3.1.1', 'rel/release-3.1.2'],
  'hadoop' : ['rel/release-2.6.4', 'rel/release-2.7.2', 'rel/release-2.8.0',  'rel/release-2.9.0', 'rel/release-2.10.0', 'rel/release-3.0.0', 'rel/release-3.1.0', 'rel/release-3.2.0', 'rel/release-3.3.0'],
}
key = "hive"

tags = tags_dict[key]
for t in itertools.combinations(tags,2):
  log_fn = "log/" + key + "_" +  t[0].replace("/","-") + "--" + t[1].replace("/","-") + ".log"
  cmd = "python3 traverse_files.py --proto --app ../{} --v1 {} --v2 {} > {}".format(key, t[0], t[1], log_fn)
  os.system(cmd)
