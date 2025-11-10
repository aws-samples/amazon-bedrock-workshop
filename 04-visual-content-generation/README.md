# Module 4 - Visual Content Generation

## Overview

This module provides a comprehensive introduction to visual content generation using Amazon Bedrock's multimodal foundation models. You'll learn how to generate images, create videos, and build intelligent search applications using embeddings that understand both text and images.

## What You'll Learn

In this module, you will:

- Generate multimodal embeddings for images and text
- Build semantic search applications with visual content
- Create high-quality images with Amazon Nova Canvas
- Generate studio-grade videos with Amazon Nova Reel
- Implement text-to-image and image-to-image generation
- Use inpainting, outpainting, and image variation techniques
- Create text-to-video and image-to-video content
- Apply visual AI to real-world marketing scenarios

## Notebooks

### 01-multimodal-embeddings.ipynb

Learn to work with multimodal embeddings:

1. **Setup** - Configure Bedrock client and dependencies
2. **Generate Embeddings** - Create embeddings for images and text
3. **Build Index** - Store embeddings for efficient retrieval
4. **Semantic Search** - Query images using text or images
5. **Similarity Scoring** - Calculate and rank search results
6. **Applications** - Build recommendation and search systems

### 02-nova-canvas.ipynb

Master image generation with Amazon Nova Canvas:

1. **Text-to-Image** - Generate images from text prompts
2. **Image Variations** - Create different versions of images
3. **Inpainting** - Edit specific parts of images with masks
4. **Outpainting** - Extend image boundaries
5. **Subject Consistency** - Maintain consistent subjects across images
6. **Brand Integration** - Apply specific colors and styles
7. **Product Visualization** - Create marketing materials

**Use Case**: Generate visual assets for Octank dog food company, including package designs, promotional materials, and professional ads.

### 03-nova-reel.ipynb

Create videos with Amazon Nova Reel:

1. **Setup** - Configure S3 and async invocation
2. **Text-to-Video** - Generate videos from text descriptions
3. **Image-to-Video** - Animate static images with text guidance
4. **Job Management** - Track and retrieve async video generation
5. **Video Processing** - Download and display generated videos
6. **Marketing Content** - Create dynamic product showcases

**Use Case**: Produce short video ads for Octank dog food using both text prompts and product images.

## Prerequisites

To run the notebooks in this module, you will need:

- Python 3.10+
- AWS credentials with permissions to:
  - Access Amazon Bedrock
  - Read/write to Amazon S3 (for video generation)
  - Invoke async operations (for video generation)
- The following models enabled in your Amazon Bedrock Console:
  - Amazon Titan Multimodal Embeddings G1
  - Amazon Titan Image Generator G1 (V2)
  - Amazon Nova Canvas
  - Amazon Nova Reel

### Additional Permissions for Video Generation

For Nova Reel (03-nova-reel.ipynb), ensure your execution role has:
- `bedrock:InvokeModel`
- `bedrock:GetAsyncInvoke`
- `bedrock:ListAsyncInvokes`
- `s3:PutObject`
- `s3:GetObject`

## Key Capabilities

### Multimodal Embeddings
- Encode text, images, or both into the same semantic space
- Build intelligent search and recommendation systems
- Support for multiple embedding dimensions
- Enterprise-ready with bias mitigation

### Image Generation (Nova Canvas)
- Text-to-image generation
- Image variations and style transfer
- Inpainting with masks
- Outpainting for boundary extension
- Subject consistency across generations
- High-quality, photorealistic outputs

### Video Generation (Nova Reel)
- Text-to-video creation
- Image-and-text to video
- Up to 2-minute videos in 6-second segments
- 1280x720 resolution at 24 FPS
- Studio-grade quality
- Async generation for longer content

## Use Cases

This module demonstrates practical applications for:
- **Marketing & Advertising** - Create product visuals and video ads
- **E-commerce** - Generate product images and demonstrations
- **Content Creation** - Produce visual assets at scale
- **Search & Discovery** - Build intelligent image search systems
- **Brand Management** - Maintain consistent visual identity
- **Product Visualization** - Showcase products in various contexts

## Contributing

We welcome community contributions! Please ensure your sample aligns with [AWS best practices](https://aws.amazon.com/architecture/well-architected/), and please update the **Contents** section of this README file with a link to your sample, along with a description.
