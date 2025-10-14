# 工具开发辅助脚本

本目录包含用于 AIECS 工具开发和维护的验证脚本，帮助开发者确保工具质量和 Schema 自动生成的有效性。

## 📋 脚本列表

### 1. 类型注解检查器 (`check_type_annotations.py`)

检查工具方法的类型注解完整性，确保所有方法都有完整的类型注解（参数类型 + 返回类型）。

**用途**：
- 验证新开发的工具是否有完整的类型注解
- 检查现有工具的类型注解覆盖率
- 为自动 Schema 生成提供基础保障

**命令**：
```bash
# 检查所有工具
aiecs-tools-check-annotations

# 检查特定工具
aiecs-tools-check-annotations pandas

# 检查多个工具
aiecs-tools-check-annotations pandas chart image

# 显示详细的改进建议
aiecs-tools-check-annotations pandas --verbose
```

**输出示例**：
```
====================================================================================================
工具类型注解检查器
====================================================================================================

✅ pandas: 38/38 方法有完整类型注解 (100.0%)

⚠️ my_tool: 5/10 方法有完整类型注解 (50.0%)

  需要改进的方法:
    ✗ process_data: 无类型注解
    ⚠ filter_records: 部分类型注解
      → 为参数 'condition' 添加类型注解
      → 添加返回类型注解

====================================================================================================
总体统计: 43/48 方法有完整类型注解 (89.6%)
====================================================================================================
```

### 2. Schema 质量验证器 (`validate_tool_schemas.py`)

验证自动生成的 Schema 质量，识别需要改进的文档字符串。

**用途**：
- 验证 Schema 自动生成是否成功
- 评估生成的 Schema 描述质量
- 指导开发者改进文档字符串

**命令**：
```bash
# 验证所有工具
aiecs-tools-validate-schemas

# 验证特定工具
aiecs-tools-validate-schemas pandas

# 显示详细的改进建议
aiecs-tools-validate-schemas pandas --verbose

# 显示示例 Schema
aiecs-tools-validate-schemas pandas --show-examples
```

**输出示例**：
```
====================================================================================================
工具 Schema 质量验证器
====================================================================================================

✅ chart
  方法数: 3
  成功生成 Schema: 3 (100.0%)
  描述质量: 100.0%
  综合评分: 100.0% (A (优秀))

❌ pandas
  方法数: 38
  成功生成 Schema: 38 (100.0%)
  描述质量: 0.0%
  综合评分: 66.7% (D (需改进))

  需要改进的方法 (38 个):

    filter:
      💡 在文档字符串的 Args 部分为参数 'records' 添加描述
      💡 在文档字符串的 Args 部分为参数 'condition' 添加描述

====================================================================================================
总体统计:
  方法数: 41
  Schema 生成率: 41/41 (100.0%)
  描述质量: 7.3%
====================================================================================================
```

## 🚀 工具开发工作流

### 新工具开发流程

1. **编写工具类**
   ```python
   from aiecs.tools.base_tool import BaseTool
   from typing import List, Dict
   
   class MyTool(BaseTool):
       """My custom tool"""
       
       def process(self, data: List[Dict], threshold: float = 0.5) -> Dict:
           """
           Process data with threshold.
           
           Args:
               data: Input data to process
               threshold: Processing threshold (0.0 to 1.0)
           
           Returns:
               Processing results
           """
           pass
   ```

2. **检查类型注解**
   ```bash
   aiecs-tools-check-annotations my_tool --verbose
   ```
   
   确保所有方法都有 ✅ 标记。

3. **验证 Schema 质量**
   ```bash
   aiecs-tools-validate-schemas my_tool --show-examples
   ```
   
   目标：综合评分 ≥ 80% (B 良好)

4. **改进文档字符串**
   
   根据验证器的建议，改进文档字符串：
   ```python
   def process(self, data: List[Dict], threshold: float = 0.5) -> Dict:
       """
       Process data with threshold filtering.
       
       Args:
           data: List of data records to process (each record is a dict)
           threshold: Minimum confidence threshold for filtering (0.0 to 1.0, default: 0.5)
       
       Returns:
           Dictionary containing processed results and statistics
       """
       pass
   ```

5. **重新验证**
   ```bash
   aiecs-tools-validate-schemas my_tool
   ```

### 现有工具维护流程

1. **定期检查**
   ```bash
   # 每次修改工具后运行
   aiecs-tools-check-annotations my_tool
   aiecs-tools-validate-schemas my_tool
   ```

2. **批量检查**
   ```bash
   # 检查所有工具
   aiecs-tools-check-annotations
   aiecs-tools-validate-schemas
   ```

3. **持续改进**
   - 优先改进评分 < 80% 的工具
   - 为通用描述（如 "Parameter xxx"）添加有意义的说明

## 📊 质量标准

### 类型注解标准

- ✅ **优秀 (100%)**：所有方法都有完整类型注解
- ⚠️ **良好 (80-99%)**：大部分方法有完整类型注解
- ❌ **需改进 (<80%)**：缺少大量类型注解

### Schema 质量标准

- ✅ **A (优秀) ≥90%**：Schema 生成成功，描述质量高
- ⚠️ **B (良好) 80-89%**：Schema 生成成功，描述质量中等
- ⚠️ **C (中等) 70-79%**：Schema 生成成功，描述质量较低
- ❌ **D (需改进) <70%**：Schema 生成失败或描述质量差

## 💡 最佳实践

### 1. 完整的类型注解

```python
# ✅ 好的示例
def filter(self, records: List[Dict], condition: str) -> List[Dict]:
    pass

# ❌ 不好的示例
def filter(self, records, condition):  # 缺少类型注解
    pass

def filter(self, records: List[Dict], condition):  # 部分缺失
    pass
```

### 2. 详细的文档字符串

使用 Google 或 NumPy 风格：

```python
# ✅ Google 风格（推荐）
def filter(self, records: List[Dict], condition: str) -> List[Dict]:
    """
    Filter DataFrame based on a condition.
    
    Args:
        records: List of records to filter (each record is a dict)
        condition: Filter condition using pandas query syntax (e.g., 'age > 30')
    
    Returns:
        Filtered list of records
    """
    pass

# ✅ NumPy 风格
def filter(self, records: List[Dict], condition: str) -> List[Dict]:
    """
    Filter DataFrame based on a condition.
    
    Parameters
    ----------
    records : List[Dict]
        List of records to filter (each record is a dict)
    condition : str
        Filter condition using pandas query syntax (e.g., 'age > 30')
    
    Returns
    -------
    List[Dict]
        Filtered list of records
    """
    pass
```

### 3. 有意义的描述

```python
# ❌ 不好的描述
"""
Args:
    records: Parameter records
    condition: Parameter condition
"""

# ✅ 好的描述
"""
Args:
    records: List of data records to filter (each record contains fields like 'name', 'age', etc.)
    condition: Filter condition using pandas query syntax (e.g., 'age > 30 and status == "active"')
"""
```

### 4. 处理复杂类型

```python
from typing import List, Dict, Optional, Union
import pandas as pd

# ✅ 使用标准类型
def process(self, data: List[Dict]) -> Dict:
    pass

# ✅ pandas 类型会自动映射为 Any
def process(self, df: pd.DataFrame) -> pd.DataFrame:
    pass

# ✅ 可选参数
def process(self, data: List[Dict], config: Optional[Dict] = None) -> Dict:
    pass
```

## 🔧 故障排查

### 问题：类型注解检查失败

**原因**：缺少类型注解或使用了不支持的类型

**解决**：
1. 为所有参数添加类型注解
2. 添加返回类型注解
3. 使用标准类型（List, Dict, str, int, float, bool 等）

### 问题：Schema 生成失败

**原因**：
- 方法没有参数（除了 self）→ 这是正常的，无需 Schema
- 类型注解不完整 → 运行类型注解检查器
- 使用了不支持的类型 → 会自动映射为 Any

### 问题：描述质量低

**原因**：文档字符串缺少 Args 部分或描述不详细

**解决**：
1. 添加文档字符串的 Args 部分
2. 为每个参数添加详细描述
3. 使用 Google 或 NumPy 风格

## 📚 相关文档

- [Schema Generator 技术文档](../../../docs/TOOLS/TOOLS_SCHEMA_GENERATOR.md)
- [LangChain Adapter 技术文档](../../../docs/TOOLS/TOOLS_LANGCHAIN_ADAPTER.md)
- [BaseTool 开发指南](../../../docs/TOOLS/TOOLS_BASE_TOOL.md)

## 🤝 贡献

如果你发现这些工具有改进空间，欢迎提交 PR 或 Issue！

---

**维护者**: AIECS Tools Team  
**最后更新**: 2025-10-02

