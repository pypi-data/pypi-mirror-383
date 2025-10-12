"""基础测试文件"""
import sys
import os

# 添加src到Python路径，以便测试可以找到模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_import():
    """测试是否可以正常导入主模块"""
    try:
        import moon_cloud_coder
        assert hasattr(moon_cloud_coder, '__version__')
        assert hasattr(moon_cloud_coder, 'app')
        print("✓ 主模块导入成功")
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        raise

if __name__ == "__main__":
    test_import()
    print("所有测试通过！")