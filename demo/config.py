from dsdl.objectio import LocalFileReader, AliOSSFileReader

local_config = dict(
    UnstructuredObjectFileReader=LocalFileReader(working_dir="/Users/wangbin1/data"),
)

ali_oss_kwargs = dict(access_key_secret="9Gh6sZIQGlNCrjrIxdJFfWqc78VceS",
                      endpoint="http://oss-cn-shanghai.aliyuncs.com",
                      access_key_id="LTAI5t7nbhDigaSxs1sGVer8",
                      bucket_name="shlab-open",
                      working_dir="COCO2017Instance/standard/dsdl_demo/")

# 阿里云OSS读取的配置字典
ali_oss_config = dict(
    UnstructuredObjectFileReader=AliOSSFileReader(**ali_oss_kwargs)
)
