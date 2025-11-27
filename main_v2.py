import lzma
import re
import sys

import requests


def get_apt_dependencies(package_name, release="plucky", arch="amd64"):
    url = f"http://archive.ubuntu.com/ubuntu/dists/{release}/main/binary-{arch}/Packages.xz"

    try:
        response = requests.get(url)
        response.raise_for_status()

        decompressed_data = lzma.decompress(response.content).decode("utf-8")

        package_pattern = f"Package: {package_name}\n(.*?)\n\n"
        match = re.search(package_pattern, decompressed_data, re.DOTALL)

        if match:
            package_info = match.group(1)
            deps_match = re.search(r"Depends: (.*)", package_info)
            if deps_match:
                dependencies = deps_match.group(1).split(", ")
                return dependencies
        return None

    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# Парсинг аргументов командной строки
package = None
url = None
test_mode = False

i = 1
while i < len(sys.argv):
    if sys.argv[i] == "--package" and i + 1 < len(sys.argv):
        package = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == "--url" and i + 1 < len(sys.argv):
        url = sys.argv[i + 1]
        i += 2
    elif sys.argv[i] == "--test-mode":
        test_mode = True
        i += 1
    else:
        i += 1

errors = []

if not package:
    errors.append("Не указан --package")
elif not package.strip():
    errors.append("Имя пакета не может быть пустым")

if not url:
    errors.append("Не указан --url")
elif not url.strip():
    errors.append("URL/путь не может быть пустым")

if errors:
    for error in errors:
        print(error)
    sys.exit(1)

if test_mode:
    dependencies = ["gcc", "make", "binutils", "python3-dev"]
else:
    dependencies = get_apt_dependencies(package)

if dependencies:
    for dep in dependencies:
        print(dep)
else:
    print("Зависимости не найдены или произошла ошибка")