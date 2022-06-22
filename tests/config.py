from dsdl.objectio import LocalFileReader, AliOSSFileReader

helloworld_config = dict(
    UnstructuredObjectFileReader=LocalFileReader(working_dir=""),
)

ali_oss_kwargs = dict(access_key_secret="xxx",
                      endpoint="http://oss-cn-shanghai.aliyuncs.com",
                      access_key_id="xxx",
                      bucket_name="shlab-open",
                      working_dir="BDD100KImages/test_dsdl/")

helloworld_ali_oss_config = dict(
    UnstructuredObjectFileReader=AliOSSFileReader(**ali_oss_kwargs)
)

