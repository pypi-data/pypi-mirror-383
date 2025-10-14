from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos import CosServiceError, CosClientError
from qcloud_cos.cos_threadpool import SimpleThreadPool
import io
import contextlib
import sys
import os
from PIL import Image

@contextlib.contextmanager
def SuppressPrint():
    """
    A context manager to temporarily suppress print statements.

    Usage:
    with SuppressPrint():
        noisy_function()
    """
    original_stdout = sys.stdout
    with open(os.devnull, 'w') as devnull:
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = original_stdout
            

def _split_cospath(cos_path: str) -> tuple:
    """
    Split the given COS file path into its components.

    Args:
    path (str): The COS file path to be split.

    Returns:
    tuple: A tuple containing the bucket name, prefix, and file name.
    """
    split_path = cos_path.split("/")
    bucket_name = split_path[0]
    prefix = "/".join(split_path[1:-1])
    file_name = split_path[-1]
    return bucket_name, prefix, file_name

def _split_cosdir(cos_dir: str) -> tuple:
    """
    Split the given COS directory into its components.

    Args:
    path (str): The COS directory to be split.

    Returns:
    tuple: A tuple containing the bucket name, prefix.
    """
    if cos_dir.endswith("/"):
        split_dir = cos_dir.split("/")[:-1]
    else:
        split_dir = cos_dir.split("/")
    bucket_name = split_dir[0]
    prefix = "/".join(split_dir[1:])
    return bucket_name, prefix

########################################################
# List
########################################################

def list_all_files_under_cos_dir(
    cos_dir: str, 
    config: dict,
    verbose: bool = True, 
    return_path_only: bool = True
) -> list:
    bucket_name, prefix = _split_cosdir(cos_dir)
    
    if verbose:
        print(f"Listing all files under {bucket_name}/{prefix}...")
        
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)
    
    marker = ""
    count = 0
    all_info = []
    while True:
        if verbose:
            print(f"{count * 1000} files have been found!", end="\r")
        response = client.list_objects(
            Bucket=bucket_name,
            Prefix=prefix,
            Marker=marker
            )
        if 'Contents' in response:
            all_info.extend(response['Contents'])
        if response['IsTruncated'] == 'false':
            break 
        marker = response['NextMarker']
        count += 1
    if verbose:
        print(f"Total {len(all_info)} files have been found!")
        
    if not return_path_only:
        return all_info
    else:
        return [f"{bucket_name}/{file['Key']}" for file in all_info]


########################################################
# Check
########################################################

def check_cos_path_exist(
    cos_path,
    config
):
    """
    Check if the given COS path exists.
    Input:
        cos_path: str, the path of the COS file
        config: dict, the configuration of the COS client
    Output:
        bool, True if the file exists, False otherwise
    """
    bucket_name, prefix, file_name = _split_cospath(cos_path)
    object_key = f"{prefix}/{file_name}"
    
    config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(config)
    
    response = client.object_exists(
        Bucket=bucket_name,
        Key=object_key
    )
    return response

########################################################
# Delete File and Directory
########################################################
def delete_cos_file(cos_path: str, config: dict):
    bucket_name, prefix, file_name = _split_cospath(cos_path)
    key = f"{prefix}/{file_name}"
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)

    response = client.delete_object(
        Bucket=bucket_name,
        Key=key
    )
    return response


def delete_cos_dir(
    cos_dir: str,
    config: dict
):
    def delete_files(file_infos, client):

        # 构造批量删除请求
        delete_list = []
        for file in file_infos:
            delete_list.append({"Key": file['Key']})

        response = client.delete_objects(Bucket=bucket_name, Delete={"Object": delete_list})
        # print(response)
        
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)
    bucket_name, prefix = _split_cosdir(cos_dir)
    pool = SimpleThreadPool()
    marker = ""
    while True:
        file_infos = []
        response = client.list_objects(Bucket=bucket_name, Prefix=prefix, Marker=marker, MaxKeys=100)

        if "Contents" in response:
            contents = response.get("Contents")
            file_infos.extend(contents)
            pool.add_task(delete_files, file_infos, client)

        # 列举完成，退出
        if response['IsTruncated'] == 'false':
            break

        # 列举下一页
        marker = response["NextMarker"]

    pool.wait_completion()
        
    return None   


########################################################
# Download File and Directory
########################################################

def download_cos_file(
    cos_path: str,
    local_file_path: str,
    config: dict,
    part_size: int = 1,
    max_thread: int = 30,
    enable_crc: bool = False,
    num_retry: int = 10,
    **kwargs
):
    bucket_name, prefix, file_name = _split_cospath(cos_path)
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)

    response = client.download_file(
        Bucket=bucket_name,
        Key=f"{prefix}/{file_name}",
        DestFilePath=local_file_path,
        PartSize=part_size,
        MAXThread=max_thread,
        EnableCRC=enable_crc,
        **kwargs
    )

    # 使用高级接口断点续传，失败重试时不会下载已成功的分块(这里重试10次)
    for i in range(0, num_retry):
        try:
            response = client.download_file(
                Bucket=bucket_name,
                Key=f"{prefix}/{file_name}",
                DestFilePath=local_file_path,
                PartSize=part_size,
                MAXThread=max_thread,
                EnableCRC=enable_crc,
                **kwargs
            )
            break
        except CosClientError or CosServiceError as e:
            print(e)
            
    return response


def download_cos_dir(
    cos_dir: str,
    local_dir: str,
    config: dict, 
    max_thread: int = 30
):
    bucket_name, prefix = _split_cosdir(cos_dir)
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)
    delimiter = ''
    
    filepaths = list_all_files_under_cos_dir(cos_dir, config, return_path_only=True, verbose=False)
    file_infos = sorted(filepaths)
        
        
    pool = SimpleThreadPool(num_threads=max_thread)
    
    for cos_path in file_infos:
        # 文件下载 获取文件到本地
        filename = cos_path.split("/")[-1]
        local_path = f"{local_dir}/{filename}"
        os.makedirs(local_dir, exist_ok=True)

        # skip dir, no need to download it
        if str(local_path).endswith("/"):
            continue
        bucket_name, prefix, filename = _split_cospath(cos_path)
        key = f"{prefix}/{filename}"
        pool.add_task(client.download_file, bucket_name, key, local_path)

    pool.wait_completion()



########################################################
# Upload File and Directory
########################################################

def save_img2cos(
    img: Image.Image,
    cos_save_path: str,
    config: dict,
) -> dict:
    img_stream = io.BytesIO()
    img.save(img_stream, format="JPEG")
    img_stream.seek(0)
    return upload_stream2cos(img_stream, cos_save_path, config)

def upload_stream2cos(
    stream: io.BytesIO,
    cos_save_path: str,
    config: dict,
) -> dict:
    
    bucket_name, prefix, file_name = _split_cospath(cos_save_path)
    key_name = f"{prefix}/{file_name}"
    
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)
    
    response = client.put_object(
        Bucket=bucket_name,
        Body=stream,
        Key=key_name,
    )
    return response


def upload_file2cos(
    local_file_path: str,
    cos_save_path: str,
    config: dict, 
    part_size: int = 1, 
    max_thread: int = 30, 
    enable_md5: bool = False
) -> dict:
    """
    Upload a local file to COS.

    Args:
    local_file_path (str): The path to the local file to upload.
    cos_save_path (str): The path to save the file on TOS.
    config (dict): The configuration for the COS client.
    part_size (int): The size of the part to upload.(Unit: MB)
    max_thread (int): The maximum number of threads to use.
    enable_md5 (bool): Whether to enable MD5 checksum.

    """
    bucket_name, prefix, file_name = _split_cospath(cos_save_path)
    key_name = f"{prefix}/{file_name}"
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])
    client = CosS3Client(cos_config)
    
    response = client.upload_file(
        Bucket=bucket_name,
        LocalFilePath=local_file_path,
        Key=key_name,
        PartSize=part_size,
        MAXThread=max_thread,
        EnableMD5=enable_md5
    )
    return response


def upload_dir2cos(
    local_upload_dir: str,
    cos_dir: str,
    config: dict,
    part_size: int = 1,
    max_thread: int = 30,
    enable_md5: bool = False,
    flat: bool = False,
    verbose: bool = False,
    check_exist: bool = True,
):
    """
    Upload a local directory to COS.

    Args:
        local_upload_dir (str): The local directory to upload.
        cos_dir (str): The COS directory to upload to.
        config (dict): The configuration for the COS client.
        part_size (int): The size of the part to upload.(Unit: MB)
        max_thread (int): The maximum number of threads to use.
        enable_md5 (bool): Whether to enable MD5 checksum.
        flat (bool): Whether to upload the files flatly.
        verbose (bool): Whether to print verbose information.
    """
    bucket_name, prefix = _split_cosdir(cos_dir)
    cos_config = CosConfig(Region=config['region'], SecretId=config['secret_id'], SecretKey=config['secret_key'])  # 获取配置对象
    client = CosS3Client(cos_config)

    bucket_name, prefix = _split_cosdir(cos_dir)

    # 创建上传的线程池
    pool = SimpleThreadPool()
    # 创建线程池时若不指定线程数则默认为5。线程数可通过参数指定，例如指定线程数为10：
    # pool = SimpleThreadPool(num_threads=10)
    for path, dir_list, file_list in os.walk(local_upload_dir):
        for file_name in file_list:
            local_filepath = os.path.join(path, file_name)
            if flat:
                cosObjectKey = os.path.join(prefix, file_name)
            else:
                parent_dir = path.split('/')[-1]
                cosObjectKey = os.path.join(prefix, parent_dir, file_name)
                
                
            # 判断 COS 上文件是否存在
            exists = False
            if check_exist:
                try:
                    response = client.head_object(Bucket=bucket_name, Key=cosObjectKey)
                    exists = True
                except CosServiceError as e:
                    if e.get_status_code() == 404:
                        exists = False
                    else:
                        if verbose:
                            print("Error happened, reupload it.")
                            
                            
            if check_exist and not exists:
                if verbose:
                    print("File %s not exists in cos, upload it", local_filepath)
                pool.add_task(client.upload_file,
                    Bucket=bucket_name,
                    Key=cosObjectKey,
                    LocalFilePath=local_filepath,
                    PartSize=part_size,
                    MAXThread=max_thread,
                    EnableMD5=enable_md5
                )


    pool.wait_completion()
    result = pool.get_result()
    if not result['success_all']:
        if verbose:
            print("Not all files upload successed. you should retry")
    else:
        if verbose:
            print("All files upload successed.")
    return result 




