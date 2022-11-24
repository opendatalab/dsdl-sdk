# CLI command examples

## config

config command contains two subcommands:

1. **config repo**
2. **config storage**

list all the available keys could be set

```shell
$dsdl config -k
```

list all the current **dict-like** configuration

```shell
$dsdl config -l
```

same as -l, but **expand nested dict** for better reading

```shell
$dsdl config -ll 
```

For detailed configuration, use the following sub commands:

### dsdl config repo

Suppose you want to set another repo other than the default one, following command is a **one-liner**.

```shell
$dsdl config repo --repo-name My_repo --repo-username zhangsan --repo-userpswd 123456--repo-service http://10.1.1.1:8080
```

Or you can set **username/password/service_url**  individually, but you have to specify the **reponame** during each action.

This will raise error due to absense of the **reponame**

```shell
$dsdl config repo --repo-username zhangsan
```

The **one-liner** above is highly recommended, user individual input when you need to modify some configuration.

### dsdl config storage

Suppose you have alternate storage options(**S3 bucket/ sftp**), using the following command to finish its configuration.

For **s3**:
The input of **--storage-credentials** takes two arguments:
**accesskey secretkey**

```shell
$dsdl config storage --storage-name MyAliOss --storage-path s3://mybucket/datasets/CV --storage-credentials myaccesskey mysecretkey --storage-endpoint http://123.4.5.6
```

For **sftp**:
**--storage-endpoint** is not neccessary.
The input of **--storage-credentials** takes two arguments:
**user password**

```shell
$dsdl config storage --storage-name Mysftp --storage-path sftp://ip:port --storage-credentials user password
```

After all this, you can use the following command to check if all the settings was done right.

```shell
$dsdl config -l
```
