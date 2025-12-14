from dataclasses import dataclass, fields, MISSING
from typing import Type, get_type_hints, Any
from pydantic import BaseModel, create_model, Field


def dataclass_to_pydantic(dc_class: Type) -> Type[BaseModel]:
    """
    将 dataclass 转换为 Pydantic BaseModel

    Args:
        dc_class: dataclass 类型

    Returns:
        对应的 Pydantic BaseModel 类型
    """
    if not hasattr(dc_class, '__dataclass_fields__'):
        raise TypeError(f"{dc_class.__name__} 不是一个 dataclass")

    # 获取类型注解
    type_hints = get_type_hints(dc_class)

    # 构建字段定义
    field_definitions = {}

    for field in fields(dc_class):
        field_name = field.name
        field_type = type_hints.get(field_name, Any)

        # 处理默认值
        if field.default is not MISSING:
            # 有默认值
            field_definitions[field_name] = (field_type, field.default)
        elif field.default_factory is not MISSING:
            # 有默认工厂函数
            field_definitions[field_name] = (field_type, Field(default_factory=field.default_factory))
        else:
            # 必填字段
            field_definitions[field_name] = (field_type, ...)

    # 创建 Pydantic 模型
    pydantic_model = create_model(
        dc_class.__name__,
        __base__=BaseModel,
        **field_definitions
    )

    return pydantic_model


# 使用示例
if __name__ == "__main__":
    from typing import Optional, List


    # 定义一个 dataclass
    @dataclass
    class User:
        name: str
        age: int
        email: Optional[str] = None
        tags: List[str] = None
        is_active: bool = True


    # 转换为 Pydantic BaseModel
    UserModel = dataclass_to_pydantic(User)

    # 测试
    print("=" * 50)
    print("转换后的 Pydantic 模型:")
    print(UserModel.model_json_schema())

    print("\n" + "=" * 50)
    print("创建实例:")
    user1 = UserModel(name="张三", age=25)
    print(f"user1: {user1}")
    print(f"user1 JSON: {user1.model_dump_json()}")

    print("\n" + "=" * 50)
    user2 = UserModel(name="李四", age=30, email="lisi@example.com", tags=["python", "ai"])
    print(f"user2: {user2}")

    # 验证功能
    print("\n" + "=" * 50)
    print("验证功能测试:")
    try:
        invalid_user = UserModel(name="王五", age="not a number")
    except Exception as e:
        print(f"验证错误（预期）: {type(e).__name__}")

    # 更复杂的示例
    print("\n" + "=" * 50)
    print("嵌套 dataclass 示例:")


    @dataclass
    class Address:
        city: str
        street: str
        zip_code: str = "000000"


    @dataclass
    class Employee:
        name: str
        employee_id: int
        address: Address
        salary: float = 0.0


    AddressModel = dataclass_to_pydantic(Address)
    EmployeeModel = dataclass_to_pydantic(Employee)

    address = AddressModel(city="北京", street="中关村大街1号")
    employee = EmployeeModel(
        name="赵六",
        employee_id=1001,
        address=address.model_dump(),
        salary=15000.0
    )
    print(f"employee: {employee}")
    print(f"employee JSON: {employee.model_dump_json(indent=2)}")
