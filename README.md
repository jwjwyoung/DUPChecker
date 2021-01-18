# Serialization Library Compatibility Checker

## What can SLCChecker do:
1. incompatibility of protocol file created through PortocolBuffer or Thrift across versions:


    (1). Add/delete required field. 

    (2). A  required field has been changed to optional. According to the guidelines in protobuf official website, Required Is Forever You should be very careful about marking fields as required. If at some point you wish to stop writing or sending a required field, it will be problematic to change the field to an optional field - old readers will consider messages without this field to be incomplete and may reject or drop them unintentionally. You should consider writing application-specific custom validation routines for your buffers instead.

    (3). The tag number of a field has been changed, the protobuf guidelines suggests each field in the message definition has a unique number. These numbers are used to identify your fields in the message binary format, and should not be changed once your message type is in use. 

    For (1) and (3), SLCChecker will output ERROR info, and for (2), SLCChecker will output WARNING info. 

2. incompatibility of thrift file across versions.

## How to use

1. check protobuf file

    `python3 slcchecker.py  --app path_app --proto --v1 old_version_tag --v2 new_version_tag`

    i.e.

    `python3 slcchecker.py  --app hbase --proto --v1 rel/2.2.6 --v2 rel/2.3.3`

2. check thrift file

    `python3 slcchecker.py  --app path_app --thrift --v1 old_version_tag --v2 new_version_tag`
