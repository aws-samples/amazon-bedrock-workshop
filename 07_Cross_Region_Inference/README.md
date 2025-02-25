# Scalable inference with Amazon Bedrock
Amazon Bedrock provides easy access to leading foundation models from multiple model providers. Bedrock offers various inference mechanisms to consume these models. Following different types are available in Bedrock:
* On-demand inference – The standard option for inference. Involves invoking a model in a specific AWS Region.
* Cross-region inference – The opt-in feature allowing access to foundation models beyond a single region. It involves invoking an inference profile, an abstraction over foundation models deployed across a set of AWS Regions, to which it can route inference requests. It helps in increasing throughput and improves resiliency by dynamically routing requests (to the regions defined in the inference profile), depending on user traffic and demand.
* Provisioned Throughput – The option to purchase dedicated compute. It involves purchasing a dedicated level of throughput for a model in a specific AWS Region. Provisioned Throughput quotas depend on the number of model units that you purchase.


## Contents
This folder contains examples to get you started with various inference patterns for Amazon Bedrock. Choose from the examples below to learn more:
1. [Getting Started with Cross-region Inference](Getting_started_with_Cross-region_Inference.ipynb) - Introductory sample to help you understand how to use cross-region inference feature from Amazon Bedrock.


## Contributing

We welcome community contributions! Please ensure your sample aligns with AWS [best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
