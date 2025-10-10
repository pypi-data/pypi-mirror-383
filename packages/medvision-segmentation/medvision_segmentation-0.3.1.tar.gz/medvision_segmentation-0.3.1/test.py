import os
import re

# 根目录
root_dir = "LITS2017"

# 子目录列表
splits = ["train", "val", "test"]

# 遍历每个数据子集
for split in splits:
    image_dir = os.path.join(root_dir, split, "image")
    label_dir = os.path.join(root_dir, split, "label")

    for folder in [image_dir, label_dir]:
        if not os.path.exists(folder):
            print(f"⚠️ 跳过不存在的目录: {folder}")
            continue

    # 遍历图像文件
    for filename in os.listdir(image_dir):
        if filename.endswith(".nii"):
            # 提取数字 ID，例如 volume-90.nii → 90
            match = re.search(r"(\d+)", filename)
            if not match:
                print(f"❌ 无法解析ID: {filename}")
                continue

            case_id = int(match.group(1))
            case_id_str = f"{case_id:05d}"  # 补齐 5 位，如 00090

            # 构造新文件名
            new_image_name = f"case_{case_id_str}_image.nii"
            new_label_name = f"case_{case_id_str}_label.nii"

            # 原文件路径
            old_image_path = os.path.join(image_dir, filename)
            old_label_path = os.path.join(label_dir, f"segmentation-{case_id}.nii")

            # 新文件路径
            new_image_path = os.path.join(image_dir, new_image_name)
            new_label_path = os.path.join(label_dir, new_label_name)

            # 重命名
            os.rename(old_image_path, new_image_path)
            if os.path.exists(old_label_path):
                os.rename(old_label_path, new_label_path)
            else:
                print(f"⚠️ 缺少标签文件: {old_label_path}")

    print(f"✅ {split} 集处理完成")