# easy_cos

让数据流动变得简单！Make data flow!
```bash
pip install easy_cos==0.1.0 --index-url https://pypi.tuna.tsinghua.edu.cn/simple
#
pip install easy_cos==0.1.0 --index-url https://pypi.org/simple  #清华等其他镜像源可能同步慢
```


这个库的开发是包含了大部分常用的 cos 脚本操作，避免许多重复代码。以及让很多新入职的同事能够快速用起来我们的数据。、
<br>
<br>
<br>

## 准备工作
```bash
# 安装 SDK
COS_CONFIG = {
    'secret_id': f'{os.environ["COS_SECRET_ID"]}',
    'secret_key': f'{os.environ["COS_SECRET_KEY"]}',
    'region': f'{os.environ["COS_REGION"]}',
}
```

<br>
<br>
<br>


# 场景一（list all files under a cos dir）：

```python
from easy_cos import list_all_files_under_cos_dir

list_all_files_under_cos_dir(
    cos_dir="cos://bucket_name/prefix",
    config=COS_CONFIG,
    verbose=True,
    return_path_only=True,
)
```

# 场景二（check if a cos path exists）：

```python
from easy_cos import check_cos_path_exist

check_cos_path_exist(
    cos_path="cos://bucket_name/prefix/file.txt",
    config=COS_CONFIG,
)
``` 

# 场景三（delete a cos file）：

```python
from easy_cos import delete_cos_file

delete_cos_file(
    cos_path="cos://bucket_name/prefix/file.txt",
    config=COS_CONFIG,
)
```

# 场景四（delete a cos dir）：

```python
from easy_cos import delete_cos_dir

delete_cos_dir(
    cos_dir="cos://bucket_name/prefix",
    config=COS_CONFIG,
)
```

# 场景五（download a cos file）：

```python
from easy_cos import download_cos_file

download_cos_file(
    cos_path="cos://bucket_name/prefix/file.txt",
    local_file_path="local/path/file.txt",
    config=COS_CONFIG,
)
```

# 场景六（download a cos dir）：

```python
from easy_cos import download_cos_dir

download_cos_dir(
    cos_dir="cos://bucket_name/prefix",
    local_dir="local/path",
    config=COS_CONFIG,
)
```


# 场景七（save an image to cos）：

```python
from easy_cos import save_img2cos

save_img2cos(
    img=Image.open("image.jpg"),
    cos_save_path="cos://bucket_name/prefix/image.jpg",
    config=COS_CONFIG,
)
```

# 场景八（upload a file to cos）：

```python
from easy_cos import upload_file2cos

upload_file2cos(
    local_file_path="local/path/file.txt",
    cos_save_path="cos://bucket_name/prefix/file.txt",
    config=COS_CONFIG,
)
```


# 场景九（upload a dir to cos）：

```python
from easy_cos import upload_dir2cos

upload_dir2cos(
    local_upload_dir="local/path",
    cos_dir="cos://bucket_name/prefix",
    config=COS_CONFIG,
)