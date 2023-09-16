# Amazon Bedrock ワークショップ

開発者とソリューションビルダーを対象としたこのハンズオンワークショップでは、[Amazon Bedrock](https://aws.amazon.com/bedrock/) を通じて基盤モデル (FM) を活用する方法を紹介します。

Amazon Bedrockは完全マネージド型のサービスで、サードパーティプロバイダーとAmazonのFMへのアクセスを提供します。APIを介して利用できます。Bedrockでは、さまざまなモデルから選択して、ユースケースに最適なモデルを見つけることができます。

この一連のラボでは、生成AI についてお客様に見られる最も一般的な使用パターンをいくつか調べます。テキストや画像を生成し、生産性を向上させて組織に価値をもたらす手法を紹介します。これは、メールの作成、テキストの要約、質問への回答、チャットボットの構築、画像の作成に役立つ基盤モデルを活用することで実現されます。Bedrock API や SDK のほか、[LangChain](https://python.langchain.com/docs/get_started/introduction) や [FAISS](https://faiss.ai/index.html) などのオープンソースソフトウェアを使用して、これらのパターンを実装する実践的な経験を積むことができます。

ラボには以下が含まれます。

*   **Text Generation** [完了までの推定時間-30 分]
*   **Text Summarization** [完了までの推定時間-30 分]
*   **Questions Answering** [完了までの推定時間-45 分]
*   **Chatbot** [完了までの推定時間-45 分]
*   **Image Generation** [完了までの推定時間-30 分]

<div align="center"></div>

これらの [ワークショップのウェブサイトにあるステップバイステップのガイド付きインストラクション](https://catalog.us-east-1.prod.workshops.aws/workshops/a4bdb007-5600-4368-81c5-ff5b4154f518/en-US) も参照できます。

## はじめに

### ノートブック環境を選択してください

このワークショップは **Python notebooks** のシリーズとして提供され、任意の環境から実行できます。

*   豊富な AI/ML 機能を備えたフルマネージド環境では、[SageMaker Studio](https://aws.amazon.com/sagemaker/studio/) の使用をお勧めします。すぐに使い始めるには、[ドメインクイックセットアップの説明](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html) を参照してください。
*   フルマネージドでありながらより基本的なエクスペリエンスを実現するには、代わりに [SageMaker ノートブックインスタンスの作成](https://docs.aws.amazon.com/sagemaker/latest/dg/howitworks-create-ws.html) を使用できます。
*   既存の (ローカルまたはその他の) ノートブック環境を使用したい場合は、[AWS を呼び出すための認証情報](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) があることを確認してください。

### Bedrock の AWS IAM アクセス権限を有効にする

ノートブック環境から引き継ぐ AWS ID (SageMaker の [_Studio/notebook Execution Role_](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html)、または自己管理型ノートブックの場合はロールや IAM ユーザーの場合もあります) には、Amazon Bedrock サービスを呼び出すのに十分な [AWS IAM のアクセス許可](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html) が必要です。

BedrockにIDへのアクセスを許可するには、次の方法があります。

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

このサービスはプレビュー段階であるため、Amazon Bedrock SDK は [Python 用 AWS SDK-boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) の標準リリースにはまだ含まれていません。以下のスクリプトを実行して、Bedrock をテストするためのカスタム SDK ホイールをダウンロードして抽出します。

```sh
bash ./download-dependencies.sh
```

このスクリプトでは `dependencies` フォルダが作成され、関連する SDK がダウンロードされますが、まだ `pip install` は作成されません。

これで、ラボノートを探索する準備ができました！Bedrock SDK のインストール方法、クライアントの作成方法、Python から API の呼び出しを開始する方法の詳細については、[00_Intro/Bedrock_boto3_Setup.ipynb](00_Intro/bedrock_boto3_setup.ipynb) をご覧ください。

## コンテンツ

このリポジトリには、Bedrock Architecture Patterns ワークショップのノートブックサンプルが含まれています。ノートブックは以下のようにモジュール別に整理されています。

### イントロ

*   [シンプルな Bedrock の使い方](./00_Intro/bedrock_boto3_setup.ipynb): このノートブックには、boto3 クライアントのセットアップと bedrock の基本的な使い方が記載されています。

### 世代

*   [boto3 を使ったシンプルなユースケース](./01_Generation/00_generate_w_bedrock.ipynb): このノートブックでは、Amazon Bedrock を使用してテキストを生成します。Amazon Titan モデルを boto3 で直接消費する方法を示します。
*   [LangChainを使ったシンプルなユースケース](./01_Generation/01_zero_shot_generation.ipynb): 次に、同じタスクを実行しますが、一般的なフレームワーク LangChain を使用します
*   [コンテキストを追加した生成](./01_Generation/02_contextual_generation.ipynb): 次に、レスポンスを改善するために、コンテキストを追加してプロンプトを強化することで、これをさらに進めます。

### 要約

*   [小さなテキストの要約](./02_Summarization/01.small-text-summarization-claude.ipynb): このノートブックでは、Bedrockを使って小さなテキストを要約するという簡単な作業を行います。
*   [長文の要約](./02_Summarization/02.long-text-summarization-titan.ipynb): 要約する内容が大きくなり、モデルの最大トークンを超えるため、上記の方法は機能しない可能性があります。このノートブックでは、ファイルを小さなチャンクに分割し、各チャンクを要約し、その要約をまとめる方法を紹介します。

### 質問応答

*   [コンテキスト付きの簡単な質問](./03_QuestionAnswering/00_qa_w_bedrock_titan.ipynb): このノートブックは、モデルを直接呼び出して、与えられたコンテキストで質問に答える簡単な例を示しています。
*   [Retrieval Augmented Generation による質問への回答](./03_QuestionAnswering/01_qa_w_rag_claude.ipynb): Retrival Augmented Generation (RAG) と呼ばれるアーキテクチャを実装することで、上記のプロセスを改善できます。RAG は言語モデルの外部 (ノンパラメトリック) からデータを取得し、取得した関連データをコンテキストに追加することでプロンプトを拡張します。

### チャットボット

*   [クロードを使ったチャットボット](./04_Chatbot/00_Chatbot_Claude.ipynb): このノートブックには Claude を使っているチャットボットが描かれています
*   [Titan を使用するチャットボット](./04_Chatbot/00_Chatbot_Titan.ipynb): このノートブックには Titan を使っているチャットボットが描かれています

### テキストから画像へ

*   [Stable Diffusion による画像生成](./05_Image/Bedrock%20Stable%20Diffusion%20XL.ipynb): このノートブックは、Stable Diffusion モデルを使用した画像生成のデモンストレーションです
