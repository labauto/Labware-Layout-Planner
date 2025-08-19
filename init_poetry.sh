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

    # 対象ディレクトリに移動して poetry コマンドを実行
    (
        cd "$target_dir" || exit 1

        # poetry install を実行
        PYENV_VERSION=$python_version pyenv exec poetry install
        echo "Executed 'poetry install' in $target_dir"

        # requirements.txt がある場合、内容を読み込んで各パッケージを poetry add で追加
        if [ -f "requirements.txt" ]; then
            while IFS= read -r package || [ -n "$package" ]; do
                # 空行やコメント行をスキップ
                if [[ -z "$package" ]] || [[ "$package" =~ ^# ]]; then
                    continue
                fi
                PYENV_VERSION=$python_version pyenv exec poetry add "$package"
            done < "requirements.txt"
            echo "Added packages from requirements.txt via 'poetry add' in $target_dir"
        fi
    )
done
