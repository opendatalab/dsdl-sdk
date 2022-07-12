from dsdl.objectio import LocalFileReader, AliOSSFileReader

local_config = dict(
    UnstructuredObjectFileReader=LocalFileReader(working_dir=""),
)

ali_oss_kwargs = dict(access_key_secret="9Gh6sZIQGlNCrjrIxdJFfWqc78VceS",
                      endpoint="http://oss-cn-shanghai.aliyuncs.com",
                      access_key_id="LTAI5t7nbhDigaSxs1sGVer8",
                      bucket_name="shlab-open",
                      working_dir="PASCALVOC2012Detection/standard/0.3/")

# 阿里云OSS读取的配置字典
ali_oss_config = dict(
    UnstructuredObjectFileReader=AliOSSFileReader(**ali_oss_kwargs)
)
