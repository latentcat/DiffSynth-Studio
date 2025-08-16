# Qwen Image Training with SwanLab Support

本文档介绍如何在Qwen Image训练中使用SwanLab进行实验跟踪和可视化。

## 安装SwanLab

首先需要安装SwanLab：

```bash
pip install swanlab
```

## 使用方法

### 1. 基本用法

在训练脚本中添加以下参数：

```bash
--use_swanlab  # 启用SwanLab日志记录
--swanlab_mode cloud  # 使用云端模式（可选：local 或 cloud）
```

### 2. 完整示例

参考 `lora/Qwen-Image-SwanLab.sh` 脚本：

```bash
accelerate launch examples/qwen_image/model_training/train.py \
  --dataset_base_path data/example_image_dataset \
  --dataset_metadata_path data/example_image_dataset/metadata.csv \
  --max_pixels 1048576 \
  --dataset_repeat 50 \
  --model_id_with_origin_paths "Qwen/Qwen-Image:transformer/diffusion_pytorch_model*.safetensors,Qwen/Qwen-Image:text_encoder/model*.safetensors,Qwen/Qwen-Image:vae/diffusion_pytorch_model.safetensors" \
  --learning_rate 1e-4 \
  --num_epochs 5 \
  --remove_prefix_in_ckpt "pipe.dit." \
  --output_path "./models/train/Qwen-Image_lora" \
  --lora_base_model "dit" \
  --lora_target_modules "to_q,to_k,to_v,add_q_proj,add_k_proj,add_v_proj,to_out.0,to_add_out,img_mlp.net.2,img_mod.1,txt_mlp.net.2,txt_mod.1" \
  --lora_rank 32 \
  --use_gradient_checkpointing \
  --dataset_num_workers 8 \
  --find_unused_parameters \
  --use_swanlab \
  --swanlab_mode cloud
```

### 3. 记录的指标

启用SwanLab后，训练过程中会自动记录以下指标：

- `train_loss`: 每步的训练损失
- `epoch_avg_loss`: 每个epoch的平均损失
- `learning_rate`: 学习率变化
- `epoch`: 当前epoch
- `step`: 全局步数

### 4. 参数说明

- `--use_swanlab`: 布尔标志，启用SwanLab日志记录
- `--swanlab_mode`: SwanLab模式
  - `cloud`: 云端模式，数据上传到SwanLab云端
  - `local`: 本地模式，数据保存在本地
  - `None`: 默认模式

### 5. 查看结果

训练开始后，SwanLab会提供一个Web界面链接，您可以通过该链接实时查看训练进度和指标可视化。

### 6. 注意事项

1. 确保已安装SwanLab：`pip install swanlab`
2. 如果使用云端模式，需要先注册SwanLab账号
3. 损失值每10步打印一次到控制台
4. 每个epoch结束时会打印平均损失
5. 只有主进程会进行日志记录，避免多进程重复记录

### 7. 故障排除

如果遇到"SwanLab not installed"错误，请安装SwanLab：

```bash
pip install swanlab
```

如果不想使用SwanLab，只需移除 `--use_swanlab` 参数即可。