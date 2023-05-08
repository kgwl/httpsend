# httpsend

This program allows sending many HTTP requests and saving the responses to files.

#### Installation

```
git clone https://github.com/kgwl/httpsend

pip3 install -r requirements.txt
```

#### Example usage:
```
└─$ python3 httpsend.py -u https://google.com -E headers -X GET
[200]  /foo/bar/httpsend-output/google.com.GET.headers saved
```
