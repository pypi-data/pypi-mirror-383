from mcp.server.fastmcp import FastMCP
import zzy_schedule_quality.service.quality as quality

# Create an MCP server
mcp = FastMCP("Quality")

@mcp.tool()
def get_quality_rectification_list() -> list:
    """用于查寻质量整改数据, 查询结果将以列表形式返回。列表中每个对象包含了id(整改单id、name(整改单名称)、date(创建日期)、userName(创建人名称）等信息。"""
    return quality.quality_rectification_list()

@mcp.tool()
def get_quality_rectification_detail(record_id: str) -> dict:
    """用于查询质量整改-单条记录的详细情况。查询时需要指定记录的id, 方法根据id返回对应的记录详情(包含基本信息(name-整改单名称、date-检查日期、checkUserName-检查人员)、问题情况-problemDetail(discoveryAddress-发现地址、详细位置-detailPosition、问题描述-problemDescription)等信息。"""
    return quality.quality_rectification_detail(record_id)

def main() -> None:
    print("Hello from zzy-schedule-quality!")
    mcp.run(transport="stdio")
