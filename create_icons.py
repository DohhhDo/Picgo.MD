#!/usr/bin/env python3
"""
图标生成器 - 将 MEOW.png 转换为多尺寸软件图标
支持 Windows (.ico)、macOS (.icns) 和 Linux (.png) 格式
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFilter
import argparse


class IconGenerator:
    """图标生成器类"""

    # 常用图标尺寸
    ICON_SIZES = {
        "windows": [16, 24, 32, 48, 64, 128, 256, 512],
        "macos": [16, 32, 64, 128, 256, 512, 1024],
        "linux": [16, 22, 24, 32, 48, 64, 128, 256, 512],
        "web": [16, 32, 48, 96, 144, 192, 256, 512],
        "android": [36, 48, 72, 96, 144, 192, 512],
        "ios": [29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024],
    }

    def __init__(self, source_image_path: str, output_dir: str = "icons"):
        """
        初始化图标生成器

        Args:
            source_image_path: 源图像文件路径
            output_dir: 输出目录
        """
        self.source_path = source_image_path
        self.output_dir = output_dir
        self.source_image = None

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

    def load_source_image(self):
        """加载源图像"""
        try:
            self.source_image = Image.open(self.source_path).convert("RGBA")
            print(f"✅ 成功加载源图像: {self.source_path}")
            print(f"   原始尺寸: {self.source_image.size}")
            return True
        except Exception as e:
            print(f"❌ 加载源图像失败: {e}")
            return False

    def create_rounded_icon(
        self, image: Image.Image, corner_radius: int = None
    ) -> Image.Image:
        """
        创建圆角图标

        Args:
            image: 输入图像
            corner_radius: 圆角半径，如果为 None 则自动计算

        Returns:
            圆角图像
        """
        if corner_radius is None:
            corner_radius = min(image.size) // 8  # 自动计算圆角半径

        # 创建圆角遮罩
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius=corner_radius, fill=255)

        # 应用遮罩
        result = Image.new("RGBA", image.size, (0, 0, 0, 0))
        result.paste(image, (0, 0))
        result.putalpha(mask)

        return result

    def resize_image(
        self, size: int, quality: int = Image.Resampling.LANCZOS
    ) -> Image.Image:
        """
        调整图像大小

        Args:
            size: 目标尺寸
            quality: 重采样质量

        Returns:
            调整后的图像
        """
        if not self.source_image:
            raise ValueError("源图像未加载")

        # 保持宽高比
        original_size = self.source_image.size
        if original_size[0] != original_size[1]:
            # 如果不是正方形，先裁剪为正方形
            min_size = min(original_size)
            left = (original_size[0] - min_size) // 2
            top = (original_size[1] - min_size) // 2
            right = left + min_size
            bottom = top + min_size
            square_image = self.source_image.crop((left, top, right, bottom))
        else:
            square_image = self.source_image

        # 调整大小
        resized = square_image.resize((size, size), quality)
        return resized

    def generate_png_icons(self, sizes: list = None, platform: str = "windows"):
        """
        生成 PNG 格式图标

        Args:
            sizes: 尺寸列表
            platform: 平台类型
        """
        if sizes is None:
            sizes = self.ICON_SIZES.get(platform, self.ICON_SIZES["windows"])

        platform_dir = os.path.join(self.output_dir, platform)
        os.makedirs(platform_dir, exist_ok=True)

        print(f"\n🎨 生成 {platform.upper()} PNG 图标...")

        for size in sizes:
            try:
                resized = self.resize_image(size)

                # 为某些平台创建圆角图标
                if platform in ["android", "ios"]:
                    resized = self.create_rounded_icon(resized)

                filename = f"icon_{size}x{size}.png"
                filepath = os.path.join(platform_dir, filename)
                resized.save(filepath, "PNG", optimize=True)
                print(f"   ✅ {filename}")

            except Exception as e:
                print(f"   ❌ 生成 {size}x{size} 失败: {e}")

    def generate_ico_file(self, sizes: list = None):
        """
        生成 Windows ICO 文件

        Args:
            sizes: 尺寸列表
        """
        if sizes is None:
            sizes = self.ICON_SIZES["windows"]

        print(f"\n🎨 生成 Windows ICO 文件...")

        try:
            # 准备不同尺寸的图像
            images = []
            for size in sizes:
                resized = self.resize_image(size)
                images.append(resized)

            # 保存为 ICO 文件
            ico_path = os.path.join(self.output_dir, "app_icon.ico")
            images[0].save(
                ico_path,
                format="ICO",
                sizes=[(img.width, img.height) for img in images],
                append_images=images[1:],
            )
            print(f"   ✅ app_icon.ico (包含 {len(images)} 个尺寸)")

        except Exception as e:
            print(f"   ❌ 生成 ICO 文件失败: {e}")

    def generate_icns_file(self, sizes: list = None):
        """
        生成 macOS ICNS 文件 (需要额外的库)

        Args:
            sizes: 尺寸列表
        """
        if sizes is None:
            sizes = self.ICON_SIZES["macos"]

        print(f"\n🎨 生成 macOS ICNS 文件...")

        try:
            # 创建临时 PNG 文件
            temp_dir = os.path.join(self.output_dir, "temp_iconset")
            os.makedirs(temp_dir, exist_ok=True)

            # 生成 iconset 所需的文件
            iconset_files = {
                16: "icon_16x16.png",
                32: "icon_16x16@2x.png",
                32: "icon_32x32.png",
                64: "icon_32x32@2x.png",
                128: "icon_128x128.png",
                256: "icon_128x128@2x.png",
                256: "icon_256x256.png",
                512: "icon_256x256@2x.png",
                512: "icon_512x512.png",
                1024: "icon_512x512@2x.png",
            }

            for size in sizes:
                if size in iconset_files:
                    resized = self.resize_image(size)
                    filename = iconset_files[size]
                    filepath = os.path.join(temp_dir, filename)
                    resized.save(filepath, "PNG")

            print(f"   ✅ 已生成 iconset 文件到 {temp_dir}")
            print(f"   💡 使用 iconutil 命令生成 ICNS: iconutil -c icns {temp_dir}")

        except Exception as e:
            print(f"   ❌ 生成 ICNS 文件失败: {e}")

    def generate_all_formats(self):
        """生成所有格式的图标"""
        if not self.load_source_image():
            return False

        print(f"\n🚀 开始生成多尺寸图标...")
        print(f"输出目录: {os.path.abspath(self.output_dir)}")

        # 生成各平台 PNG 图标
        for platform in ["windows", "macos", "linux", "web", "android", "ios"]:
            self.generate_png_icons(platform=platform)

        # 生成 ICO 文件
        self.generate_ico_file()

        # 生成 ICNS 相关文件
        self.generate_icns_file()

        print(f"\n🎉 图标生成完成！")
        print(f"📁 输出目录: {os.path.abspath(self.output_dir)}")

        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="多尺寸图标生成器")
    parser.add_argument("source", help="源图像文件路径")
    parser.add_argument("-o", "--output", default="icons", help="输出目录 (默认: icons)")
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux", "web", "android", "ios", "all"],
        default="all",
        help="目标平台",
    )

    args = parser.parse_args()

    # 检查源文件是否存在
    if not os.path.exists(args.source):
        print(f"❌ 源文件不存在: {args.source}")
        return 1

    # 创建图标生成器
    generator = IconGenerator(args.source, args.output)

    # 生成图标
    if args.platform == "all":
        success = generator.generate_all_formats()
    else:
        success = generator.load_source_image()
        if success:
            if args.platform == "windows":
                generator.generate_png_icons(platform="windows")
                generator.generate_ico_file()
            else:
                generator.generate_png_icons(platform=args.platform)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
