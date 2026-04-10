# Custom Models

Model customization in Amazon Bedrock enhances foundation models for specific use cases through three methods:

**Distillation**: Transfers knowledge from a larger "teacher" model to a smaller, efficient "student" model using automated data synthesis for fine-tuning.

**Fine-tuning**: Uses labeled data to train a model for improved task-specific performance by adjusting its parameters.

**Continued Pre-training**: Exposes a model to domain-specific unlabeled data to refine its knowledge and adapt to specialized inputs.

## Dataset Validation
Before creating a custom model job (fine-tuning or distillation) in Amazon Bedrock, use the provided script to validate your dataset.

| Custom Model Job Type |  Model | Dataset Validation Script |
|-----------------------|--------|---------------------------|
| Fine-Tuning           | Llama  | [llama models validation script](./bedrock-fine-tuning/meta-llama/dataset_validation) |
| Fine-Tuning           | Nova   | [Nova models validation script](./bedrock-fine-tuning/nova/understanding/dataset_validation) |
| Fine-Tuning           | Haiku  | [Haiku models validation script](./bedrock-fine-tuning/claude-haiku/DataValidation) |
| Distillation          | supported (teacher, student) model | [Model Distillation validation script](./model_distillation/dataset-validation) |



## Contents
- [Fine-Tuning](./bedrock-fine-tuning) - Exmaple showing how different LLMs can be fine tuned onto Amazon Bedrock.
- [Model Distillation](./model_distillation) - Exmaple showing how different  LLMs can be distilled onto Amazon Bedrock.
- [import_models](./import_models) - Exmaple showing how different Opensource LLMs can be imported onto Amazon Bedrock.


## Contributing

We welcome community contributions! Please ensure your sample aligns with  [AWS best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
