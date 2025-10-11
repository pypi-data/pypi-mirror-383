# src/kusosort/cpp/CMakeLists.txt

cmake_minimum_required(VERSION 3.15)
project(kusosort_cpp)

find_package(pybind11 REQUIRED)

# Python拡張モジュールを定義
# 第一引数がモジュール名 (Python側で import _kusosort_impl となる)
# 第二引数がソースファイル
pybind11_add_module(_kusosort_impl kusosort.cpp)

# 生成されるモジュールをライブラリディレクトリにインストール
install(TARGETS _kusosort_impl DESTINATION kusosort)