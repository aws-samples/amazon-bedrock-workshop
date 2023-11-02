# ラボ 2 - Summarization (文章要約)

## 概要

文章要約は、テキストドキュメントから最も関連性の高い情報を抽出し、簡潔で一貫性のある形式で表示する自然言語処理 (NLP) 手法です。

要約は、次の例のように、モデルにプロンプトの指示を送信し、モデルにテキストの要約を求めることで機能します。

```xml
Please summarize the following text:

<text>
Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Sem fringilla ut morbi tincidunt augue interdum velit euismod in. 
Quis hendrerit dolor magna eget est.
<text>
```

モデルに要約タスクを実行させるために、プロンプトエンジニアリングと呼ばれる手法を使用します。これは、データを処理するときに期待されることと応答に関する指示を（プレーンテキストで）モデルに送信します。これについて詳しく知りたい場合は、 [こちら](https://www.promptingguide.ai/) をご覧ください。

## 関係性

多くの人はやるべき作業が多く多忙です。会議に出席したり、記事やブログを読んだりする必要がある場合、要約は重要なテーマについて最新の情報を得るのに役立つ優れたテクニックです。
このモジュールでは、Amazon Bedrock API を使用して大小のテキストをすばやく要約できるため、理解が簡単になります。
このデモンストレーションの目的は、以下のような一般的なユースケースシナリオにおいて要約を実現する技術と再現する方法を示すことです。

* 学術論文
* 文字起こし:
  * ビジネスコール後   
  * コールセンター
* 法的文書
* 財務報告書

## 対象読者

このモジュールは、Python に精通している開発者なら誰でも、データサイエンティストやその他の技術者でも実行できます。

## パターン

このワークショップでは、要約に関する以下のパターンを学ぶことができます。

1. [小さなファイルによるテキストの要約](./01.small-text-summarization-claude.ja.ipynb)

    ![small text](./images/41-text-simple-1.png)

2. [抽象的な文章要約](./02.long-text-summarization-titan.ja.ipynb)

    ![large text](./images/42-text-summarization-2.png)
