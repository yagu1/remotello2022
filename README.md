# remotello
Remote Tello control method using redis

# remotelloとは？

Ryze Tech. のTelloシリーズを、インターネット越しに操縦するためのシステムです。

# どんな仕組み？

Telloを直接インターネットに接続することは出来ないので、
TelloにつながったPCがインターネット上のサーバに画像を転送し、
クライアントPCはサーバから画像を受け取ります。

逆に、クライアントPCはTelloを操縦するコマンドをサーバに書き込み、
TelloにつながったPCはサーバーからコマンドを受け取ってTelloに送信します。

具体的には以下の図のようになります。

![system](https://user-images.githubusercontent.com/55542434/135413352-afe179c3-6a30-4903-83c9-c98ea3e047ab.png)

# サーバーは？

使用しているのは Redis データベースサーバーです。
メモリ(RAM)を使うデータベースなので、読み書きが高速です。

## データベースって難しそう。。。

Redisは一般的なSQL文を使用するデータベースサーバではありません。

```
r.set("名前",data)       # データの書き込み(rはサーバーのハンドルクラス)
data = r.get("名前")     # データの読み込み
```
このように、"名前"とデータを紐づけてset/getするだけなので、利用は簡単です。

MQTTのtopic名とpayloadデータみたいな気分で使えます。

SQLと比べて簡単ですが、"名前"の中に入っているデータがどんな形式なのかは、送受する人間が予め知っておかなければいけません。

## セキュリティは？

現在はredisサーバにセキュリティをかけていません。。。今後の課題です。

なので、悪意のある人間がTelloの映像を取ったり、飛行中に別のコマンドを送ったりする可能性があります。

ssl/tlsのオレオレ認証ぐらいはかけたほうが良いですかね。。。


# 開発環境

- Telloに接続するPC：　無線LAN(Telloへの接続用)、有線または無線LAN(インターネット接続用）
- クライアントPC：　有線または無線LAN(インターネット接続用）

- 使用言語：　Python3
- 主な使用ライブラリ：　OpenCV, NumPy, Redis

**動作確認したバージョン**

- Python3 3.8.10
- opencv-pythonおよびopencv-contrib-python 4.5.3.56
- numpy 1.21.2
- redis 3.5.3

# 依存ライブラリのインストール

```
$ pip3 install opencv-python opencv-contrib-python
$ pip3 install redis
```

# このgitの構成

- client: クライアントPCで利用するプログラム
- server: Telloに接続するPCで利用するプログラム

