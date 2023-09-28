# Amazon Bedrock ワークショップ

開発者とソリューションビルダーを対象としたこのハンズオンワークショップでは、[Amazon Bedrock](https://aws.amazon.com/bedrock/) を通じて基盤モデル (FM) を活用する方法を紹介します。

Amazon Bedrock は完全マネージド型のサービスで、サードパーティプロバイダーと Amazon の FM へのアクセスを提供します。API を介して利用できます。Bedrock では、さまざまなモデルから選択して、ユースケースに最適なモデルを見つけることができます。

この一連のラボでは、生成 AI についてお客様に見られる最も一般的な使用パターンをいくつか見ていきます。テキストや画像を生成し、生産性を向上させて組織に価値をもたらす手法を紹介します。これは、メールの作成、テキストの要約、質問への回答、チャットボットの構築、画像の生成に役立つ基盤モデルを活用することで実現されます。Bedrock API や SDK のほか、[LangChain](https://python.langchain.com/docs/get_started/introduction) や [FAISS](https://faiss.ai/index.html) などのオープンソースソフトウェア (OSS) を使用して、これらのパターンを実装する実践的な経験を積むことができます。

ラボには以下が含まれます。

*   **Text Generation** [完了までの推定時間-30 分]
*   **Text Summarization** [完了までの推定時間-30 分]
*   **Questions Answering** [完了までの推定時間-45 分]
*   **Chatbot** [完了までの推定時間-45 分]
*   **Image Generation** [完了までの推定時間-30 分]
*   **Code Generation** [完了までの推定時間-30 分]

<div align="center">

![imgs/11-overview](imgs/11-overview.png "Overview of the different labs in the workshop")

</div>

これらの [ワークショップのウェブサイトにあるステップバイステップのガイド付きインストラクション](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) も参照できます。

## はじめに

### ノートブック環境を選択してください

このワークショップは **Python notebooks** のシリーズとして提供され、任意の環境から実行できます。

*   豊富な AI/ML 機能を備えたフルマネージド環境では、[SageMaker Studio](https://aws.amazon.com/sagemaker/studio/) の使用をお勧めします。すぐに使い始めるには、[ドメインクイックセットアップの説明](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html) を参照してください。
*   フルマネージドでありながらより基本的なエクスペリエンスを実現するには、代わりに [SageMaker ノートブックインスタンスの作成](https://docs.aws.amazon.com/sagemaker/latest/dg/howitworks-create-ws.html) を使用できます。
*   既存の (ローカルまたはその他の) ノートブック環境を使用したい場合は、[AWS を呼び出すための認証情報](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) があることを確認してください。

### Bedrock の AWS IAM アクセス権限を有効にする

ノートブック環境から引き継ぐ AWS ID (SageMaker の [_Studio/notebook Execution Role_](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html)、または自己管理型ノートブックの場合はロールや IAM ユーザーの場合もあります) には、Amazon Bedrock サービスを呼び出すのに十分な [AWS IAM のアクセス許可](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) が必要です。

Bedrock に ID へのアクセスを許可するには、次の方法があります。

*   [AWS IAM コンソール](https://us-east-1.console.aws.amazon.com/iam/home?#) を開いてください
*   [ロール](https://us-east-1.console.aws.amazon.com/iamv2/home?#/roles) (SageMaker を使用している場合や IAM ロールを引き受けている場合)、または [ユーザ](https://us-east-1.console.aws.amazon.com/iamv2/home?#/users) を検索してください
*   _Add Permissions > Create Inline Policy_ を選択して新しいインライン権限を添付し、_JSON_ エディターを開いて以下のポリシー例を貼り付けます。

<!---->

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockFullAccess",
                "Effect": "Allow",
                "Action": ["bedrock:*"],
                "Resource": "*"
            }
        ]
    }

> ⚠️ **Note:** Amazon SageMaker では、ノートブックの実行ロールは通常、AWS コンソールへのログインに使用したユーザーまたはロールの _separate_ になります。Amazon Bedrock 用の AWS コンソールを試してみたい場合は、コンソールのユーザー/ロールにもアクセス権限を付与する必要があります。

Bedrock のきめ細かいアクションとリソース権限の詳細については、Bedrock 開発者ガイドをご覧ください。

### ノートブックを複製して使用する

> ℹ️ **Note:** SageMaker Studio では、_File > New > Terminal_ をクリックすると「システムターミナル」を開いてこれらのコマンドを実行できます

ノートブック環境を設定したら、このワークショップリポジトリをその中に複製します。

```sh
git clone https://github.com/aws-samples/amazon-bedrock-workshop.git
cd amazon-bedrock-workshop
```

このサービスはプレビュー段階であるため、Amazon Bedrock SDK は [Python 用 AWS SDK-boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) の標準リリースにはまだ含まれていません。以下のスクリプトを実行して、Bedrock をテストするためのカスタム SDK wheel をダウンロードして抽出します。

```sh
bash ./download-dependencies.sh
```

このスクリプトでは `dependencies` フォルダが作成され、関連する SDK がダウンロードされますが、まだ `pip install` は実行されません。

これで、ラボノートを探索する準備ができました！Bedrock SDK のインストール方法、クライアントの作成方法、Python から API の呼び出しを開始する方法の詳細については、[00_Intro/Bedrock_boto3_Setup.ipynb](00_Intro/bedrock_boto3_setup.jp.ipynb) をご覧ください。

## コンテンツ

このリポジトリには、[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) のノートブックサンプルが含まれています。ノートブックは以下のようにモジュール別に整理されています。

### Intro

*   [シンプルな Bedrock の使い方](./00_Intro/bedrock_boto3_setup.ja.ipynb): このノートブックには、boto3 クライアントのセットアップと bedrock の基本的な使い方が記載されています。

### Generation (テキスト生成)

*   [boto3 を使ったシンプルなユースケース](./01_Generation/00_generate_w_bedrock.ja.ipynb): このノートブックでは、Amazon Bedrock を使用してテキストを生成します。Amazon Titan モデルを boto3 で直接利用する方法を示します。
*   [LangChainを使ったシンプルなユースケース](./01_Generation/01_zero_shot_generation.ja.ipynb): 次に、同じタスクを実行しますが、一般的なフレームワーク LangChain を使用します。
*   [コンテキストを追加した生成](./01_Generation/02_contextual_generation.ja.ipynb): 次に、レスポンスを改善するために、コンテキストを追加してプロンプトを強化することができます。

[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) の [Text Generation](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP/30-generation) をご参考ください。

### Summarization (文章要約)

*   [小さなテキストの要約](./02_Summarization/01.small-text-summarization-claude.ja.ipynb): このノートブックでは、Bedrock を使って小さなテキストを要約するという簡単な作業を行います。
*   [長文の要約](./02_Summarization/02.long-text-summarization-titan.ja.ipynb): 要約する内容が大きくなり、モデルの最大トークンを超えるため、上記の方法は機能しない可能性があります。このノートブックでは、ファイルを小さなチャンクに分割し、各チャンクを要約し、その要約をまとめる方法を紹介します。

[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) の [Text Summarization](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP/40-summarization/42-detailed-summarization) をご参考ください。

### Question Answering (質問応答)

*   [コンテキスト付きの簡単な質問](./03_QuestionAnswering/00_qa_w_bedrock_titan.ja.ipynb): このノートブックは、モデルを直接呼び出して、与えられたコンテキストで質問に答える簡単な例を示しています。
*   [Retrieval Augmented Generation による質問への回答](./03_QuestionAnswering/01_qa_w_rag_claude.ja.ipynb): Retrival Augmented Generation (RAG) と呼ばれるアーキテクチャを実装することで、上記のプロセスを改善できます。RAG は言語モデルの外部 (ノンパラメトリック) からデータを取得し、取得した関連データをコンテキストに追加することでプロンプトを拡張します。

[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) の [Question Answering](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP/50-qa) をご参考ください。

### ChatBot (チャットボット)

*   [Claude を使用するチャットボット](./04_Chatbot/00_Chatbot_Claude.ja.ipynb): このノートブックには Claude を使用するチャットボットの例が含まれています。
*   [Titan を使用するチャットボット](./04_Chatbot/00_Chatbot_Titan.ja.ipynb): このノートブックには Titan を使用するチャットボットの例が含まれています。

[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) の [Conversational Interface - Chatbots](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP/60-chatbot) をご参考ください。

### Image (画像生成)

*   [Stable Diffusion による画像生成](./05_Image/Bedrock%20Stable%20Diffusion%20XL.ja.ipynb): このノートブックは、Stable Diffusion モデルを使用した画像生成のデモンストレーションです。

[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) の [Image Generation](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP/70-image) をご参考ください。

### Code Generation (コード生成、SQL生成、コード翻訳、説明)

1. [コード生成](./06_CodeGeneration/00_code_generatation_w_bedrock.ja.ipynb): 自然言語を使用して Python コードを生成する方法を示します。データアナリストが与えられた売上 CSV データセットに対して売上分析を実行するために、Python で簡単な関数、クラス、完全なプログラムを生成するプロンプトの例を示します。

2. [Database や SQL Queryの生成](./06_CodeGeneration/01_sql_query_generate_w_bedrock.ja.ipynb) : Amazon Bedrock API を使った SQL クエリの生成に焦点を当てています。与えられたデータセットとデータベーススキーマに対して、単純な SQL 文と複雑な SQL 文の両方を生成する例が含まれています。

3. [Code の説明](./06_CodeGeneration/02_code_interpret_w_langchain.ja.ipynb) : Bedrock の基盤モデルを使って、複雑な C++ コード・スニペットの説明を生成します。複雑な C++ コード例の機能やロジックを説明するコメントやドキュメントを生成するために、入念なプロンプトを作成する方法を示しています。プロンプトは、他のプログラミング言語用に簡単に更新することができます。

4. [Code 翻訳](./06_CodeGeneration/03_code_translate_w_langchain.ja.ipynb) : Amazon Bedrock と LangChain API を使用して、C++ コードを Java に変換する方法を説明します。言語間の構文、言語構成、規約の違いを扱いながら、C++ コードを Java に移植するテクニックを示します。

[Bedrock Architecture Designe Patterns ワークショップ](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP) の [Code Generation](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/ja-JP/80-codegeneration) をご参考ください。