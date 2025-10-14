from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("bmi-calculator")

@mcp.tool()
def calculate_bmi(height: float, weight: float) -> str:
    """计算BMI值并返回健康状况评估
    
    参数:
        height: 身高（米）
        weight: 体重（千克）
    
    返回:
        BMI计算结果和健康状况评估
    """
    try:
        # 验证输入
        if height <= 0 or weight <= 0:
            return "错误：身高和体重必须为正数"
            
        # 计算BMI
        bmi = weight / (height * height)
        
        # 评估健康状况
        if bmi < 18.5:
            status = "体重过轻"
        elif bmi < 24:
            status = "体重正常"
        elif bmi < 28:
            status = "超重"
        else:
            status = "肥胖"
            
        return f"BMI值：{bmi:.1f}\n健康状况：{status}"
        
    except Exception as e:
        return f"计算出错：{str(e)}"

def main():
    """MCP 服务器入口点"""
    print("BMI计算器服务已启动...")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
