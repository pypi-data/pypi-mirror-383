"""
关系图
"""


class RelationChart:
    @staticmethod
    def relation_chart(data: dict, x_name: str = "", y_name: str = "", title="", **kwargs):
        """
        {
                    name: '系列名称，data 中数据项为单指标（单值）时也可用于显示指标名称',
                    // data 单值时
                    nodes: [
                        { name: '1', value: 2 },
                        { name: '2', value: 3 },
                    ],
                    links: [
                        // value 为保留值，用于力导向图中计算边长度
                        { source: '1', target: '2', value: 10, label: '关系名称' },
                    ],
                    unit: '单位', // 或者 unit: ['单位'], 单位将无视类目轴，从数值类型维度开始匹配
                }
        :return:
        """
        result = {
            "chart_type": "NoCartesianCoordinatesRelation",
            "title": title,
            "xName": x_name,
            "yName": y_name,
            "name": data.get("name", ""),
            "nodes": data.get("nodes", []),
            "links": data.get("links", []),
            "unit": data.get("unit", "")
        }
        if kwargs:
            result["pool"] = kwargs
        return result
