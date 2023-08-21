# 弐号機使用の地上局プログラム

種子島ロケットコンテストで使用する地上局のプログラムです
Anacondaを使ってプログラムを実行します。

## 使用環境のインストール方法

まず、`git clone`でこのリポジトリをPCにクローンします。

Anaconda Promptを開き、コピー先の仮想環境をアクティベートします。そして以下のコマンドを実行します。

```shell
conda env create -f  env1.yaml
```
を実行します。

このとき、Pythonのバージョンが`3.9`以上でないとエラーとなります。  

## 使用環境の複製方法
Anaconda Promptを開き、コピー元の環境をアクティベートします。
```shell
activate [環境名]
```
[環境名]は以下のbase部分の文字にあたります。
```shell
(base) $
```

パッケージの一覧はyamlファイルとして出力します。今いるディレクトリに保存されるので、保存したい場所に移動してから実行してください。
以下コマンドにてファイルを出力します。
```shell
conda env export > ev1.yaml
```
**パッケージを新たにインストールしたら以上の方法でファイルを生成し、新たなファイルをpushしてください**

## 機体作成に当たって使用している他のサイト

### SharePoint

<https://tdumedia.sharepoint.com/sites/astronomy>


