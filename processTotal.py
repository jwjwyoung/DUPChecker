f = open("log/hbase_total.log")
lines = f.readlines()
indices = [index for index, l in enumerate(lines) if '======== tag_old: ' in l]
i = indices[0]
optional_required = []
rest = []
add_req = []
for j in indices[1:]:
  cs = lines[i+1:j]
  for c in cs: 
    t = lines[i]
    t = t[:t.index('#change')]
    tags = t.replace("=",'').strip()
    t1 = tags.split("vs")[0][8:].strip()
    t2 = tags.split("vs")[1][9:].strip()
    if 'Changed Field' in c:
        msg = c[c.index('Message'):].strip()
        if 'optional' in c and 'required' in c:
           optional_required.append([t1,t2,msg])
        else:
           rest.append([t1,t2,msg])
    if 'Added Field' in c and 'required' in c:
        add_req.append([t1, t2, c[c.index('Message'):].strip()])
  i = j
for con in [optional_required, rest, add_req]:
  print("------------------------")
  for t1,t2,msg in con:
    print("{} | {} | {}".format(t1, t2, msg))

