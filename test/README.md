# S3FS Test Suites

## Files
| file | purpose |
| ---- | ------- |
| checksum_test.py | Verify that checksum as extended attribute functionality is working correctly |

### Running checksum_test.py test suite

The checksum test suite is written in `python3`, and uses [xattr](https://github.com/xattr/xattr) library to retrieve extended attributes from the mounted S3 bucket. We'll need these tools installed, in order to run the test suite.

The test environment also requires `docker` and `docker-compose`.
* Instructions for installing docker on Linux are available at [docs.docker.com](https://docs.docker.com/engine/installation/linux/)
* Both `docker-engine` and `docker-compose` are required.

#### Environment setup

1. Install tooling
#### Linux - Debian/Ubuntu
```
sudo apt-get install -y attr fuse python3 python3-pip
sudo pip3 install -r requirements.txt
```

#### Get the test suite

If you haven't already, you can retrieve the test suite with:
```
mkdir ~/src
cd ~/src
git clone git@github.com:c3tp/s3fs-fuse.git cc_s3fs-fuse
cd ~/src/cc_s3fs-fuse/
```

#### Build s3fs
```
./autogen.sh
./configure
make
```

#### Start local S3 API instance (minio)
```
cd test
docker-compose up -d minio
```

#### Mount the S3 filesystem
```
mkdir /tmp/s3_mount
../src/s3fs c3tp-test /tmp/s3_mount -f -o passwd_file=s3_cred_minio -o url=http://127.0.0.1:9000/ -o del_cache -o use_path_request_style -o no_check_certificate -o sigv2 -o use_xattr -o use_xattr_md5 -d -d
```
* The `s3_cred_minio` file is a text file containing a string of: `<access key id>:<secret access key>`

#### Update the S3_MOUNT variable in checksum_test.py if necessary
```
S3_MOUNT = '/tmp/s3_mount'
```

#### Run test suite
```
python3 checksum_test.py
```

#### Test cleanup
```
# Kill s3fs process

# Stop local S3 API instance (minio)
docker-compose stop minio
```

If something goes wrong with the test and you are left with an unreachable mount point, you can use the `fusermount` command.
```
fusermount -u <local mount-point here>
```
