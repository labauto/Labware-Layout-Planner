#!/bin/bash

# 現在のディレクトリを基点に探索
base_dir=$(pwd)

# カレントディレクトリ内の .python-version を検索 (-maxdepth 1 を指定)
find "$base_dir" -maxdepth 1 -type f -name ".python-version" | while read -r pyversion_file; do
    # 親ディレクトリを取得（カレントディレクトリなので必ず同一）
    target_dir=$(dirname "$pyversion_file")
    # .python-version の内容を取得
    python_version=$(cat "$pyversion_file")

    echo "Processing directory: $target_dir with Python version: $python_version"

    # pyenv に指定バージョンが存在するかチェック
    if pyenv versions --bare | grep -q "^$python_version$"; then
        echo "Python version $python_version is already installed in pyenv. Skipping installation..."
    else
        echo "Python version $python_version is not installed in pyenv. Automatically installing..."
        pyenv install "$python_version"
    fi

    # 仮想環境を作成
    PYENV_VERSION=$python_version pyenv exec python -m venv "$target_dir/.venv"
    echo "Created virtual environment in $target_dir/.venv"
    "$target_dir/.venv/bin/pip" install --upgrade pip


    # requirements.txt がある場合はパッケージをインストール
    if [ -f "$target_dir/requirements.txt" ]; then
        "$target_dir/.venv/bin/pip" install -r "$target_dir/requirements.txt"
        echo "Installed packages from requirements.txt in $target_dir"
    fi
done