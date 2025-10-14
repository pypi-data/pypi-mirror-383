from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("bmi-calculator-mcp")

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
    import sys
    
    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['--help', '-h']:
            print("BMI Calculator MCP Server")
            print("Version: 0.1.3")
            print("\nUsage: bmi-calculator-mcp")
            print("\nThis server uses stdio transport to communicate via MCP protocol.")
            print("It provides a tool to calculate BMI based on height and weight.")
            sys.exit(0)
        elif arg in ['--version', '-v']:
            print("bmi-calculator-mcp version 0.1.3")
            sys.exit(0)
    
    # 启动MCP服务器 (stdio transport)
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
