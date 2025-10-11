import rsa
import json
import base64
import hashlib
from datetime import datetime

class LicenseValidator:
    def __init__(self, public_key_path='public_key.pem'):
        """
        初始化许可证验证器
        """
        try:
            with open(public_key_path, 'rb') as f:
                self.public_key = rsa.PublicKey.load_pkcs1(f.read())
        except FileNotFoundError:
            raise FileNotFoundError(f"公钥文件 {public_key_path} 未找到")
    
    def load_license_from_file(self, file_path='license.lic'):
        """
        从文件加载许可证
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                license_data = json.load(f)
            return license_data
        except FileNotFoundError:
            raise FileNotFoundError(f"许可证文件 {file_path} 未找到")
        except json.JSONDecodeError:
            raise ValueError("许可证文件格式错误")
    
    def validate_license(self, license_data):
        """
        验证许可证的有效性
        
        Returns:
            tuple: (is_valid, message, license_info)
        """
        try:
            # 提取许可证数据和签名
            license_info = license_data['data']
            signature = base64.b64decode(license_data['signature'])
            
            # 重新创建JSON字符串（确保格式一致）
            license_json = json.dumps(license_info, ensure_ascii=False, separators=(',', ':'))
            
            # 验证签名
            try:
                rsa.verify(license_json.encode('utf-8'), signature, self.public_key)
            except rsa.VerificationError:
                return False, "许可证签名验证失败", license_info
            
            # 检查许可证是否过期
            expiration_date = datetime.fromisoformat(license_info['expiration_date'])
            if datetime.now() > expiration_date:
                return False, "许可证已过期", license_info
            
            # 检查必需字段
            # required_fields = ['customer_name', 'expiration_date', 'features']
            # for field in required_fields:
            #     if field not in license_info:
            #         return False, f"许可证缺少必需字段: {field}", license_info
            
            return True, "许可证有效", license_info
            
        except Exception as e:
            return False, f"许可证验证过程中发生错误: {str(e)}", None
    
    # def check_license_feature(self, license_info, feature):
    #     """
    #     检查许可证是否包含特定功能
    #     """
    #     if license_info and 'features' in license_info:
    #         return feature in license_info['features']
    #     return False
    
    def get_license_info(self, license_data):
        """
        获取许可证详细信息
        """
        if 'data' in license_data:
            return license_data['data']
        return None

def validate_license_file(license_file='license.lic', public_key_file='public_key.pem'):
    """
    验证许可证文件的便捷函数
    """
    try:
        # 创建验证器
        validator = LicenseValidator(public_key_file)
        
        # 加载许可证
        license_data = validator.load_license_from_file(license_file)
        
        # 验证许可证
        is_valid, message, license_info = validator.validate_license(license_data)
        
        # 输出验证结果
        print("=" * 50)
        print("许可证验证结果")
        print("=" * 50)
        
        if is_valid:
            print("✅ 状态: 有效")
            print(f"📛 客户: {license_info['customer_name']}")
            print(f"🏢 公司: {license_info.get('company', 'N/A')}")
            print(f"📧 邮箱: {license_info.get('customer_email', 'N/A')}")
            print(f"📅 签发日期: {license_info['issue_date']}")
            print(f"⏰ 到期时间: {license_info['expiration_date']}")
            # print(f"🔧 功能特性: {', '.join(license_info['features'])}")
            print(f"🔐 验证信息: {message}")
        else:
            print("❌ 状态: 无效")
            print(f"❓ 原因: {message}")
            if license_info:
                print(f"📛 客户: {license_info.get('customer_name', 'N/A')}")
                print(f"🏢 公司: {license_info.get('company', 'N/A')}")
        
        print("=" * 50)
        return is_valid, message, license_info
        
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {str(e)}")
        return False, str(e), None

def main():
    """
    主函数 - 验证许可证示例
    """
    # 验证许可证
    is_valid, message, license_info = validate_license_file('customer_license.lic', 'public_key.pem')
    
    # # 如果需要进一步检查特定功能
    # if is_valid and license_info:
    #     validator = LicenseValidator('public_key.pem')
        
    #     # 检查特定功能
    #     # features_to_check = ['premium', 'basic', 'enterprise']
    #     print("\n功能检查:")
    #     for feature in features_to_check:
    #         has_feature = validator.check_license_feature(license_info, feature)
    #         status = "✅ 支持" if has_feature else "❌ 不支持"
    #         print(f"  {feature}: {status}")

if __name__ == "__main__":
    main()