# DUPChecker: Serialization Library Compatibility Checker

## What can DUPChecker do:

DUPChecker analyzes data syntax defined using standard serialization libraries and detect incompatibility across versions, which can lead to upgrade failures. 
It focuses on two widely adopted serialization libraries, [Portocol Buffer](https://developers.google.com/protocol-buffers/docs/proto.) and [Apache Thrift](https://diwakergupta.github.io/thrift-missing-guide/).

Protocols evolve over time. Developers can update any protocol to meet the program’s need. However, certain rules have to be followed to avoid data-syntax incompatibility across versions. Particularly, the manuals of Protocol Buffer and Apache Thrift both state the following rules:

    (1). Add/delete required field. 

    (2). The tag number of a field has been changed.

    (3).  A  required field has been changed to non-required. 

Violating the first two rules will definitely lead to upgrade failures caused by syntax incompatibility, which will be referred to as `ERROR` by DUPChecker; violating the third rule may lead to failures, which will be referred to as `WARNING` by DUPChecker, if the new version generates data that does not contain its no-longer-required data member. For other type of changes such as changing field type,
DUPChecker will output `INFO` level information. 

## Installation

Checkout DUPChecker to your local machine.

    `git clone git@github.com:jwjwyoung/SLCChecker.git`

## Usage
1. Prepare the application that you would like to check the consistentcy on the same machine, suppose its path is `path_app`. 

2. Run Script

    `python3 slcchecker.py  --app path_app --filetype --v1 old_version_tag --v2 new_version_tag`

    e.g. check for proto file:

    `python3 slcchecker.py  --app hbase --proto --v1 rel/2.2.6 --v2 rel/2.3.3`
    
    e.g. check for thrift file:

    `python3 slcchecker.py  --app hbase --thrift --v1 rel/2.2.6 --v2 rel/2.3.3`

## Reproduce Experiments in the Paper Section 6.2.2

1. Checkout the required applications. 

      (1). hbase `git clone https://github.com/apache/hbase.git`
      
      (2). hdfs, yarn `git clone https://github.com/apache/hadoop.git`
      
      (3). mesos `git clone https://github.com/apache/mesos.git`

      (4). hive `git clone https://github.com/apache/hive.git`

      (5). impala `git clone https://github.com/apache/impala.git`
2. Create a log folder
    ` mkdir log`

3. Run scripts:

    `python3 run_experiment.py` 

    The results will be output to files under log folder with application's name as prefix.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## LICENSE

[MIT](https://github.com/jwjwyoung/SLCChecker/blob/master/LICENSE)
