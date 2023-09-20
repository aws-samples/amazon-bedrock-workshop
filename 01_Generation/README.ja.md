# Lab 1 - テキスト生成

## 概要

このラボでは、Amazon Bedrock で LLM を使用してテキストを生成する方法を学習します。Bedrock API を使用して LLM を使用する方法と、Bedrock と統合される LangChain フレームワークを利用する方法についても説明します。 

まず、Zero-Shot プロンプトを使用してテキストを生成します。Zero-Shot プロンプトでは、詳細なコンテキストを指定せずにテキストコンテンツを生成する指示が与えられます。Bedrock API (BoTo3) と Bedrock と LangChain の統合という 2 つのアプローチを使用して、Zero-Shot メールを生成する方法を検討します。次に、プロンプトにコンテキストを追加して生成テキストの品質を向上させる方法を示します。 

## 想定読者

Amazon Bedrock LLM を使用してテキストを生成する方法を学びたいアーキテクトおよび開発者です。 
テキスト生成のビジネスユースケースには次のようなものがあります。

- 製品の特徴とマーケティングチームの利点に基づいた製品説明の作成
- メディア記事やマーケティングキャンペーンの作成
- メールとレポートの生成

## Workshop Notebooks

カスタマーサポートエンジニアから受けたサービスについてお客様から否定的なフィードバックがあった場合は、メールで返信します。テキスト生成ワークショップには、次の 3 つのノートブックが含まれます。 
1. [Amazon Titan で E メールを生成](./00_generate_w_bedrock.ipynb) - Bedrock API を使用して Amazon Titan Text large モデルを呼び出し、顧客へのメールレスポンスを生成します。コンテキストのないゼロショットプロンプトをモデルへの指示として使用します。 
2. [Anthropic Claude で Zero-shot テキスト生成](01_zero_shot_generation.ipynb) - LangChain フレームワークと Bedrock の統合を使用して Anthropic の Claude モデルを呼び出し、顧客へのメールを生成します。コンテキストのない Zero-Shot プロンプトをモデルへの指示として使用します。
3. [LangChain を使用したコンテキスト生成](./02_contextual_generation.ipynb) - モデルにレスポンスを生成させたい顧客からの元のメールを含む追加のコンテキストをプロンプトに入力します。この例には LangChain のカスタムプロンプトテンプレートが含まれているため、実行時にプロンプトの変数値を代入できます。  

## アーキテクチャ

![Bedrock](./images/bedrock.jpg)
![Bedrock](./images/bedrock_langchain.jpg)