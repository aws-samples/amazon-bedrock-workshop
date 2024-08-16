### 8/8/2024

- New (cool) shortlink for you to remember and share! https://catalog.workshops.aws/amazon-bedrock :blob-cat-party:

- Bedrock Workshop will now be run in the new JupyterLab on SageMaker Studio and not classic Studio notebooks

- Instructions and Prereq’s have been changed in the pinned build (to be published) ... *Changes go live on 8/15* :alert:

- Weekly automated testing to make sure all labs run successfully! 

### 5/20/2024
- rolled back TTP to Titan Large in text generation
- rolled back Claude 3 to 2.1 in basic testing of RAG folder (0_ notebook)
- fixed utility file saying "Done!" every 30 seconds. Now it just does the dots. Can improve further but this should work for now.
- fixed %store etc. issues in RAG folder

### 5/10/2024
- changed pre-req notebook
    - Titan text premier (TTP) tested and works
    - Titan emb v2 tested and works
    - claude Haiku v2 instead of v2 in the messages API 
- changed few 01_Text_generation notebooks:
    - 00 now has both Claude and TTP
    - 01 now uses TTP
    - 02 now uses Claude and TTP examples
    - 03, depending on the model can answer even though for demonstration purposes we want the model to say it is unsure. Sticking to Titan Large for this, for now.
    - 04 changed readme to encourage customers to try TTP.

### 2/15/2024

- new 'basic' set up and testing which removes the need for bedrock utils folder. All notebooks now just use default boto3 bedrock/bedrock-runtime
- Some notebooks have moved as is, and others have been merged. Making sure instructions in the notebook are still correct (markdown sections) is important
- Open source examples (Langchain, Nemo)  have been moved to a separate folder. Some existing PRs can be fixed and tested directly here. Once we test it we can resolve those PRs and point to the new release.
- Fine tuning and other new feature examples are needed
- Pending Major PRs
    - https://github.com/aws-samples/amazon-bedrock-workshop/pull/194
    - https://github.com/aws-samples/amazon-bedrock-workshop/pull/187
    - https://github.com/aws-samples/amazon-bedrock-workshop/pull/149
    - https://github.com/aws-samples/amazon-bedrock-workshop/pull/107
    
    
### 2/10/2024
- Major structural changes
- working branch is BR-workshop-v2
