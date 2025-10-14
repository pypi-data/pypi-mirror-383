<div align="center">
  <picture>
    <!-- User prefers dark mode: -->
  <source srcset="https://raw.githubusercontent.com/vbti-development/onedl-mmengine/main/docs/en/_static/image/onedl-mmengine-banner-dark.png"  media="(prefers-color-scheme: dark)"/>

<img src="https://raw.githubusercontent.com/vbti-development/onedl-mmengine/main/docs/en/_static/image/onedl-mmengine-banner.png" alt="OneDL-Engine logo" height="200"/>
  </picture>

<div>&nbsp;</div>
  <div align="center">
    <a href="https://vbti.ai">
      <b><font size="5">VBTI Website</font></b>
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://onedl.ai">
      <b><font size="5">OneDL platform</font></b>
    </a>
  </div>
<div>&nbsp;</div>

[![Docs](https://img.shields.io/badge/docs-latest-blue)](https://onedl-mmpretrain.readthedocs.io/en/latest/)
[![license](https://img.shields.io/github/license/VBTI-development/onedl-mmpretrain.svg)](https://github.com/VBTI-development/onedl-mmpretrain/blob/main/LICENSE)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/onedl-mmpretrain)](https://pypi.org/project/onedl-mmpretrain/)
[![PyPI](https://img.shields.io/pypi/v/onedl-mmpretrain)](https://pypi.org/project/onedl-mmpretrain)

[![Build Status](https://github.com/VBTI-development/onedl-mmpretrain/actions/workflows/merge_stage_test.yml/badge.svg)](https://github.com/VBTI-development/onedl-mmpretrain/actions/workflows/merge_stage_test.yml)
[![open issues](https://isitmaintained.com/badge/open/VBTI-development/onedl-mmpretrain.svg)](https://github.com/VBTI-development/onedl-mmpretrain/issues)
[![issue resolution](https://isitmaintained.com/badge/resolution/VBTI-development/onedl-mmpretrain.svg)](https://github.com/VBTI-development/onedl-mmpretrain/issues)

[📘 Documentation](https://onedl-mmpretrain.readthedocs.io/en/latest/) |
[🛠️ Installation](https://onedl-mmpretrain.readthedocs.io/en/latest/get_started.html#installation) |
[👀 Model Zoo](https://onedl-mmpretrain.readthedocs.io/en/latest/modelzoo_statistics.html) |
[🆕 Update News](https://onedl-mmpretrain.readthedocs.io/en/latest/notes/changelog.html) |
[🤔 Reporting Issues](https://github.com/VBTI-development/onedl-mmpretrain/issues/new/choose)

[![Discord Logo](https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/66e3d80db9971f10a9757c99_Symbol.svg)](https://discord.gg/8DvcVRs5Pm)

</div>

## Introduction

MMPreTrain is an open source pre-training toolbox based on PyTorch.

### Major features

- Various backbones and pretrained models
- Rich training strategies (supervised learning, self-supervised learning, multi-modality learning etc.)
- Bag of training tricks
- Large-scale training configs
- High efficiency and extensibility
- Powerful toolkits for model analysis and experiments
- Various out-of-box inference tasks.
  - Image Classification
  - Image Caption
  - Visual Question Answering
  - Visual Grounding
  - Retrieval (Image-To-Image, Text-To-Image, Image-To-Text)

https://github.com/vbti-development/onedl-mmpretrain/assets/26739999/e4dcd3a2-f895-4d1b-a351-fbc74a04e904

## What's new

The VBTI development team is forking MMLabs code, making it work with
newer pytorch versions and fixing bugs. We are only a small team, so your help
is appreciated.

🌟 v1.2.0 was released in 04/01/2023

- Support LLaVA 1.5.
- Implement of RAM with a gradio interface.

🌟 v1.1.0 was released in 12/10/2023

- Support Mini-GPT4 training and provide a Chinese model (based on Baichuan-7B)
- Support zero-shot classification based on CLIP.

🌟 v1.0.0 was released in 04/07/2023

- Support inference of more **multi-modal** algorithms, such as [**LLaVA**](./configs/llava/), [**MiniGPT-4**](./configs/minigpt4), [**Otter**](./configs/otter/), etc.
- Support around **10 multi-modal** datasets!
- Add [**iTPN**](./configs/itpn/), [**SparK**](./configs/spark/) self-supervised learning algorithms.
- Provide examples of [New Config](./mmpretrain/configs/) and [DeepSpeed/FSDP with FlexibleRunner](./configs/mae/benchmarks/). Here are the documentation links of [New Config](https://onedl-mmengine.readthedocs.io/en/latest/advanced_tutorials/config.html#a-pure-python-style-configuration-file-beta) and [DeepSpeed/FSDP with FlexibleRunner](https://onedl-mmengine.readthedocs.io/en/latest/api/generated/mmengine.runner.FlexibleRunner.html#mmengine.runner.FlexibleRunner).

🌟 Upgrade from MMClassification to MMPreTrain

- Integrated Self-supervised learning algorithms from **MMSelfSup**, such as **MAE**, **BEiT**, etc.
- Support **RIFormer**, a simple but effective vision backbone by removing token mixer.
- Refactor dataset pipeline visualization.
- Support **LeViT**, **XCiT**, **ViG**, **ConvNeXt-V2**, **EVA**, **RevViT**, **EfficientnetV2**, **CLIP**, **TinyViT** and **MixMIM** backbones.

This release introduced a brand new and flexible training & test engine, but it's still in progress. Welcome
to try according to [the documentation](https://onedl-mmpretrain.readthedocs.io/en/latest/).

And there are some BC-breaking changes. Please check [the migration tutorial](https://onedl-mmpretrain.readthedocs.io/en/latest/migration.html).

Please refer to [changelog](https://onedl-mmpretrain.readthedocs.io/en/latest/notes/changelog.html) for more details and other release history.

## Installation

Below are quick steps for installation:

```shell
uv pip install
```

```shell
conda create -n onedl-lab python=3.10 pytorch==2.8.0 torchvision==0.23.0 cudatoolkit=12.9 -c pytorch -y
conda activate onedl-lab
pip install onedl-mim
git clone https://github.com/VBTI-development/onedl-mmpretrain.git
cd onedl-mmpretrain
mim install -e .
```

Please refer to [installation documentation](https://onedl-mmpretrain.readthedocs.io/en/latest/get_started.html) for more detailed installation and dataset preparation.

For multi-modality models support, please install the extra dependencies by:

```shell
mim install -e ".[multimodal]"
```

## User Guides

We provided a series of tutorials about the basic usage of MMPreTrain for new users:

- [Learn about Configs](https://onedl-mmpretrain.readthedocs.io/en/latest/user_guides/config.html)
- [Prepare Dataset](https://onedl-mmpretrain.readthedocs.io/en/latest/user_guides/dataset_prepare.html)
- [Inference with existing models](https://onedl-mmpretrain.readthedocs.io/en/latest/user_guides/inference.html)
- [Train](https://onedl-mmpretrain.readthedocs.io/en/latest/user_guides/train.html)
- [Test](https://onedl-mmpretrain.readthedocs.io/en/latest/user_guides/test.html)
- [Downstream tasks](https://onedl-mmpretrain.readthedocs.io/en/latest/user_guides/downstream.html)

For more information, please refer to [our documentation](https://onedl-mmpretrain.readthedocs.io/en/latest/).

## Model zoo

Results and models are available in the [model zoo](https://onedl-mmpretrain.readthedocs.io/en/latest/modelzoo_statistics.html).

<div align="center">
  <b>Overview</b>
</div>
<table align="center">
  <tbody>
    <tr align="center" valign="bottom">
      <td>
        <b>Supported Backbones</b>
      </td>
      <td>
        <b>Self-supervised Learning</b>
      </td>
      <td>
        <b>Multi-Modality Algorithms</b>
      </td>
      <td>
        <b>Others</b>
      </td>
    </tr>
    <tr valign="top">
      <td>
        <ul>
        <li><a href="configs/vgg">VGG</a></li>
        <li><a href="configs/resnet">ResNet</a></li>
        <li><a href="configs/resnext">ResNeXt</a></li>
        <li><a href="configs/seresnet">SE-ResNet</a></li>
        <li><a href="configs/seresnet">SE-ResNeXt</a></li>
        <li><a href="configs/regnet">RegNet</a></li>
        <li><a href="configs/shufflenet_v1">ShuffleNet V1</a></li>
        <li><a href="configs/shufflenet_v2">ShuffleNet V2</a></li>
        <li><a href="configs/mobilenet_v2">MobileNet V2</a></li>
        <li><a href="configs/mobilenet_v3">MobileNet V3</a></li>
        <li><a href="configs/swin_transformer">Swin-Transformer</a></li>
        <li><a href="configs/swin_transformer_v2">Swin-Transformer V2</a></li>
        <li><a href="configs/repvgg">RepVGG</a></li>
        <li><a href="configs/vision_transformer">Vision-Transformer</a></li>
        <li><a href="configs/tnt">Transformer-in-Transformer</a></li>
        <li><a href="configs/res2net">Res2Net</a></li>
        <li><a href="configs/mlp_mixer">MLP-Mixer</a></li>
        <li><a href="configs/deit">DeiT</a></li>
        <li><a href="configs/deit3">DeiT-3</a></li>
        <li><a href="configs/conformer">Conformer</a></li>
        <li><a href="configs/t2t_vit">T2T-ViT</a></li>
        <li><a href="configs/twins">Twins</a></li>
        <li><a href="configs/efficientnet">EfficientNet</a></li>
        <li><a href="configs/edgenext">EdgeNeXt</a></li>
        <li><a href="configs/convnext">ConvNeXt</a></li>
        <li><a href="configs/hrnet">HRNet</a></li>
        <li><a href="configs/van">VAN</a></li>
        <li><a href="configs/convmixer">ConvMixer</a></li>
        <li><a href="configs/cspnet">CSPNet</a></li>
        <li><a href="configs/poolformer">PoolFormer</a></li>
        <li><a href="configs/inception_v3">Inception V3</a></li>
        <li><a href="configs/mobileone">MobileOne</a></li>
        <li><a href="configs/efficientformer">EfficientFormer</a></li>
        <li><a href="configs/mvit">MViT</a></li>
        <li><a href="configs/hornet">HorNet</a></li>
        <li><a href="configs/mobilevit">MobileViT</a></li>
        <li><a href="configs/davit">DaViT</a></li>
        <li><a href="configs/replknet">RepLKNet</a></li>
        <li><a href="configs/beit">BEiT</a></li>
        <li><a href="configs/mixmim">MixMIM</a></li>
        <li><a href="configs/efficientnet_v2">EfficientNet V2</a></li>
        <li><a href="configs/revvit">RevViT</a></li>
        <li><a href="configs/convnext_v2">ConvNeXt V2</a></li>
        <li><a href="configs/vig">ViG</a></li>
        <li><a href="configs/xcit">XCiT</a></li>
        <li><a href="configs/levit">LeViT</a></li>
        <li><a href="configs/riformer">RIFormer</a></li>
        <li><a href="configs/glip">GLIP</a></li>
        <li><a href="configs/sam">ViT SAM</a></li>
        <li><a href="configs/eva02">EVA02</a></li>
        <li><a href="configs/dinov2">DINO V2</a></li>
        <li><a href="configs/hivit">HiViT</a></li>
        </ul>
      </td>
      <td>
        <ul>
        <li><a href="configs/mocov2">MoCo V1 (CVPR'2020)</a></li>
        <li><a href="configs/simclr">SimCLR (ICML'2020)</a></li>
        <li><a href="configs/mocov2">MoCo V2 (arXiv'2020)</a></li>
        <li><a href="configs/byol">BYOL (NeurIPS'2020)</a></li>
        <li><a href="configs/swav">SwAV (NeurIPS'2020)</a></li>
        <li><a href="configs/densecl">DenseCL (CVPR'2021)</a></li>
        <li><a href="configs/simsiam">SimSiam (CVPR'2021)</a></li>
        <li><a href="configs/barlowtwins">Barlow Twins (ICML'2021)</a></li>
        <li><a href="configs/mocov3">MoCo V3 (ICCV'2021)</a></li>
        <li><a href="configs/beit">BEiT (ICLR'2022)</a></li>
        <li><a href="configs/mae">MAE (CVPR'2022)</a></li>
        <li><a href="configs/simmim">SimMIM (CVPR'2022)</a></li>
        <li><a href="configs/maskfeat">MaskFeat (CVPR'2022)</a></li>
        <li><a href="configs/cae">CAE (arXiv'2022)</a></li>
        <li><a href="configs/milan">MILAN (arXiv'2022)</a></li>
        <li><a href="configs/beitv2">BEiT V2 (arXiv'2022)</a></li>
        <li><a href="configs/eva">EVA (CVPR'2023)</a></li>
        <li><a href="configs/mixmim">MixMIM (arXiv'2022)</a></li>
        <li><a href="configs/itpn">iTPN (CVPR'2023)</a></li>
        <li><a href="configs/spark">SparK (ICLR'2023)</a></li>
        <li><a href="configs/mff">MFF (ICCV'2023)</a></li>
        </ul>
      </td>
      <td>
        <ul>
        <li><a href="configs/blip">BLIP (arxiv'2022)</a></li>
        <li><a href="configs/blip2">BLIP-2 (arxiv'2023)</a></li>
        <li><a href="configs/ofa">OFA (CoRR'2022)</a></li>
        <li><a href="configs/flamingo">Flamingo (NeurIPS'2022)</a></li>
        <li><a href="configs/chinese_clip">Chinese CLIP (arxiv'2022)</a></li>
        <li><a href="configs/minigpt4">MiniGPT-4 (arxiv'2023)</a></li>
        <li><a href="configs/llava">LLaVA (arxiv'2023)</a></li>
        <li><a href="configs/otter">Otter (arxiv'2023)</a></li>
        </ul>
      </td>
      <td>
      Image Retrieval Task:
        <ul>
        <li><a href="configs/arcface">ArcFace (CVPR'2019)</a></li>
        </ul>
      Training&Test Tips:
        <ul>
        <li><a href="https://arxiv.org/abs/1909.13719">RandAug</a></li>
        <li><a href="https://arxiv.org/abs/1805.09501">AutoAug</a></li>
        <li><a href="mmpretrain/datasets/samplers/repeat_aug.py">RepeatAugSampler</a></li>
        <li><a href="mmpretrain/models/tta/score_tta.py">TTA</a></li>
        <li>...</li>
        </ul>
      Regression Heads:
        <ul>
        <li><a href="mmpretrain/models/heads/regression_head.py"> RegressionHead</a></li>
        <li><a href="mmpretrain/models/heads/regression_head.py"> LinearRegressionHead</a></li>
        </ul>
      </td>
  </tbody>
</table>

## Contributing

We appreciate all contributions to improve MMPreTrain.
Please refer to [CONTRUBUTING](https://onedl-mmpretrain.readthedocs.io/en/latest/notes/contribution_guide.html) for the contributing guideline.

## Acknowledgement

MMPreTrain is an open source project that is contributed by researchers and engineers from various colleges and companies. We appreciate all the contributors who implement their methods or add new features, as well as users who give valuable feedbacks.
We wish that the toolbox and benchmark could serve the growing research community by providing a flexible toolkit to reimplement existing methods and supporting their own academic research.

## Citation

If you find this project useful in your research, please consider cite:

```BibTeX
@misc{2023mmpretrain,
    title={OneDL Pre-training Toolbox and Benchmark},
    author={OneDL-MMPreTrain Contributors},
    howpublished = {\url{https://github.com/vbti-development/onedl-mmpretrain}},
    year={2025}
}
```

## License

This project is released under the [Apache 2.0 license](LICENSE).

## Projects in VBTI-development

- [MMEngine](https://github.com/vbti-development/onedl-mmengine): Foundational library for training deep learning models.
- [MMCV](https://github.com/vbti-development/onedl-mmcv): Foundational library for computer vision.
- [MMPreTrain](https://github.com/vbti-development/onedl-mmpretrain): Pre-training toolbox and benchmark.
- [MMDetection](https://github.com/vbti-development/onedl-mmdetection): Detection toolbox and benchmark.
- [MMRotate](https://github.com/vbti-development/onedl-mmrotate): Rotated object detection toolbox and benchmark.
- [MMSegmentation](https://github.com/vbti-development/onedl-mmsegmentation): Semantic segmentation toolbox and benchmark.
- [MMDeploy](https://github.com/vbti-development/onedl-mmdeploy): Model deployment framework.
- [MIM](https://github.com/vbti-development/onedl-mim): MIM installs VBTI packages.
