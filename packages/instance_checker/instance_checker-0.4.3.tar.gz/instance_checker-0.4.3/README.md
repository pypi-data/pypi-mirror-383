# Instance Checker

A simple and powerful Python utility to **count running instances of an application**.

### Usage Example

```python
from instance_checker.utils import CountHelper

helper = CountHelper(lock_dir="/tmp/my_app_locks")

print(helper.process_count("my_app"))        #> 2
print(helper.pid_file_count("my_app"))       #> 1
```

### Installation

```bash
pip install instance-checker
```

### License

MIT License — feel free to use it in any project! 🎉

### Documentation

[https://instance-checker.dkurchigin.ru/](https://instance-checker.dkurchigin.ru/)

### Author

Made with ❤️ by [@dkurchigin](https://gitverse.ru/dkurchigin)

### Gitverse

[https://gitverse.ru/dkurchigin/instance-checker](https://gitverse.ru/dkurchigin/instance-checker)