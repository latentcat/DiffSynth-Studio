from diffsynth.pipelines.qwen_image import QwenImagePipeline, ModelConfig, ControlNetInput
from PIL import Image
import torch
from modelscope import dataset_snapshot_download
import os
import glob
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time

# 配置参数
NUM_GPUS = 8  # GPU数量
TOTAL_EPOCHS = 20  # 总epoch数
MODEL_BASE_PATH = "models/train/Qwen-Image-Blockwise-ControlNet-Qr_full"

def process_epoch_on_gpu(gpu_id, epoch_list, image_folder, prompt_file):
    """
    在指定GPU上处理分配的epoch列表
    """
    device = f"cuda:{gpu_id}"
    print(f"GPU {gpu_id} 开始处理 epochs: {epoch_list}")
    
    # 支持的图片格式
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
    
    # 获取文件夹及子文件夹中的所有图片文件
    image_files = []
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(image_folder, '**', ext), recursive=True))
    
    # 读取提示词文件
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f.readlines() if line.strip()]
    
    # 处理分配给这个GPU的每个epoch
    for epoch in epoch_list:
        print(f"GPU {gpu_id} 正在处理 epoch {epoch}")
        
        # 构建模型路径
        cnpath = f"{MODEL_BASE_PATH}/epoch-{epoch}.safetensors"
        
        # 检查模型文件是否存在
        if not os.path.exists(cnpath):
            print(f"警告: 模型文件 {cnpath} 不存在，跳过 epoch {epoch}")
            continue
        
        try:
            # 初始化pipeline
            pipe = QwenImagePipeline.from_pretrained(
                torch_dtype=torch.bfloat16,
                device=device,
                model_configs=[
                    ModelConfig(model_id="Qwen/Qwen-Image", origin_file_pattern="transformer/diffusion_pytorch_model*.safetensors"),
                    ModelConfig(model_id="Qwen/Qwen-Image", origin_file_pattern="text_encoder/model*.safetensors"),
                    ModelConfig(model_id="Qwen/Qwen-Image", origin_file_pattern="vae/diffusion_pytorch_model.safetensors"),
                    ModelConfig(path=cnpath),
                ],
                tokenizer_config=ModelConfig(model_id="Qwen/Qwen-Image", origin_file_pattern="tokenizer/"),
            )
            
            # 创建输出目录
            output_dir = f"output_epoch_{epoch}"
            os.makedirs(output_dir, exist_ok=True)
            
            # 双层遍历：第一层遍历图片，第二层遍历提示词
            for i, image_path in enumerate(image_files):
                print(f"GPU {gpu_id} - Epoch {epoch} - Processing image {i+1}/{len(image_files)}: {os.path.basename(image_path)}")
                
                # 加载并调整图片大小
                controlnet_image = Image.open(image_path).resize((1328, 1328))
                
                for j, prompt in enumerate(prompts):
                    print(f"  GPU {gpu_id} - Epoch {epoch} - Using prompt {j+1}/{len(prompts)}: {prompt[:50]}...")
                    
                    # 生成图片
                    image = pipe(
                        prompt, seed=0,
                        blockwise_controlnet_inputs=[ControlNetInput(image=controlnet_image)]
                    )
                    
                    # 保存图片，使用epoch、图片名和提示词索引命名
                    image_name = os.path.splitext(os.path.basename(image_path))[0]
                    output_filename = f"{output_dir}/epoch_{epoch}_{image_name}_prompt_{j+1}.jpg"
                    image.save(output_filename)
                    print(f"    GPU {gpu_id} - Saved: {output_filename}")
            
            print(f"GPU {gpu_id} 完成 epoch {epoch} 的处理")
            
            # 清理GPU内存
            del pipe
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"GPU {gpu_id} 处理 epoch {epoch} 时出错: {str(e)}")
            continue
    
    print(f"GPU {gpu_id} 完成所有分配的epochs: {epoch_list}")
    return f"GPU {gpu_id} 完成"

def main():
    # 指定图片文件夹路径和提示词文件路径
    image_folder = "data/example_image_dataset/canny"  # 修改为你的图片文件夹路径
    prompt_file = "prompts.txt"  # 修改为你的提示词文件路径
    
    # 检查文件夹和文件是否存在
    if not os.path.exists(image_folder):
        print(f"错误: 图片文件夹 {image_folder} 不存在")
        return
    
    if not os.path.exists(prompt_file):
        print(f"错误: 提示词文件 {prompt_file} 不存在")
        return
    
    # 分配epochs到不同的GPU
    epochs = list(range(1, TOTAL_EPOCHS + 1))
    epochs_per_gpu = [[] for _ in range(NUM_GPUS)]
    
    # 轮询分配epochs到GPU
    for i, epoch in enumerate(epochs):
        gpu_id = i % NUM_GPUS
        epochs_per_gpu[gpu_id].append(epoch)
    
    print(f"Epochs分配情况:")
    for gpu_id, epoch_list in enumerate(epochs_per_gpu):
        print(f"GPU {gpu_id}: {epoch_list}")
    
    # 使用ProcessPoolExecutor并行处理
    start_time = time.time()
    
    with ProcessPoolExecutor(max_workers=NUM_GPUS) as executor:
        futures = []
        for gpu_id in range(NUM_GPUS):
            if epochs_per_gpu[gpu_id]:  # 只为有分配epochs的GPU创建任务
                future = executor.submit(
                    process_epoch_on_gpu, 
                    gpu_id, 
                    epochs_per_gpu[gpu_id], 
                    image_folder, 
                    prompt_file
                )
                futures.append(future)
        
        # 等待所有任务完成
        for future in futures:
            result = future.result()
            print(result)
    
    end_time = time.time()
    print(f"\n所有epochs处理完成! 总耗时: {end_time - start_time:.2f} 秒")

if __name__ == "__main__":
    # 设置multiprocessing启动方法
    mp.set_start_method('spawn', force=True)
    main()


# 指定图片文件夹路径和提示词文件路径
image_folder = "data/example_image_dataset/canny"  # 修改为你的图片文件夹路径
prompt_file = "prompts.txt"  # 修改为你的提示词文件路径

# 支持的图片格式
image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']

# 获取文件夹及子文件夹中的所有图片文件
image_files = []
for ext in image_extensions:
    image_files.extend(glob.glob(os.path.join(image_folder, '**', ext), recursive=True))

# 读取提示词文件
with open(prompt_file, 'r', encoding='utf-8') as f:
    prompts = [line.strip() for line in f.readlines() if line.strip()]

# 双层遍历：第一层遍历图片，第二层遍历提示词
for i, image_path in enumerate(image_files):
    print(f"Processing image {i+1}/{len(image_files)}: {image_path}")
    
    # 加载并调整图片大小
    controlnet_image = Image.open(image_path).resize((1328, 1328))
    
    for j, prompt in enumerate(prompts):
        print(f"  Using prompt {j+1}/{len(prompts)}: {prompt[:50]}...")
        
        # 生成图片
        image = pipe(
            prompt, seed=0,
            blockwise_controlnet_inputs=[ControlNetInput(image=controlnet_image)]
        )
        
        # 保存图片，使用图片名和提示词索引命名
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        output_filename = f"output_{image_name}_prompt_{j+1}.jpg"
        image.save(output_filename)
        print(f"    Saved: {output_filename}")

print("All images processed successfully!")
