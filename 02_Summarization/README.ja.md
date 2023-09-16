# ラボ 2-テキストの要約

## [概要]

テキスト要約は、テキストドキュメントから最も関連性の高い情報を抽出し、簡潔で一貫性のある形式で表示する自然言語処理 (NLP) 手法です。

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

モデルに要約タスクを実行させるために、プロンプトエンジニアリングと呼ばれる手法を使用します。これは、データを処理するときに期待されることと応答に関する指示を（プレーンテキストで）モデルに送信します。これについて詳しく知りたい場合は、[これ](https://www.promptingguide.ai/) をご覧ください。

## なぜそれが関係しているのか

たいていの人は、やることがたくさんあって忙しい。会議に出席したり、記事やブログを読んだりする必要がある場合、要約は重要なテーマについて最新の情報を得るのに役立つ優れたテクニックです。

このモジュールでは、Amazon Bedrock API を使用して大小のテキストをすばやく要約できるため、基本的な理解が簡単になります。

このデモンストレーションの目的は、他の一般的なシナリオを以下のようにまとめるために、可能性の極みと、この例を再現する方法を示すことです。

*   学術論文
*   文字起こし:
    *   ビジネスコール後
    *   コールセンター
*   法的文書
*   財務報告書

## ターゲットオーディエンス

このモジュールは、Python に精通している開発者なら誰でも、データサイエンティストやその他の技術者でも実行できます。

## パターン

このワークショップでは、要約に関する以下のパターンを学ぶことができます。

1.  [小さなファイルによるテキストの要約](./01.small-text-summarization-claude.ipynb)

    ![small text](./images/41-text-simple-1.png)

2.  [抽象的なテキスト要約](./02.long-text-summarization-titan.ipynb)

    ![large text](./images/42-text-summarization-2.png)
