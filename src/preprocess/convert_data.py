import json
import random

def generate_random_color():
    """生成随机颜色"""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgba({r}, {g}, {b}, 1)"

def convert_jsonl_to_json(input_file, output_file):
    # 读取JSONL文件
    nodes = []
    relationships = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():  # 跳过空行
                continue
            data = json.loads(line.strip())
            if data['type'] == 'node':
                nodes.append(data)
            elif data['type'] == 'relationship':
                relationships.append(data)
    
    # 创建label到颜色的映射
    label_colors = {}
    for node in nodes:
        for label in node['labels']:
            if label not in label_colors:
                label_colors[label] = generate_random_color()
    
    # 创建关系类型到颜色的映射
    relationship_colors = {}
    for rel in relationships:
        rel_type = rel['label']
        if rel_type not in relationship_colors:
            relationship_colors[rel_type] = generate_random_color()
    
    # 构建新的JSON格式
    result = {
        "rootId": nodes[0]['id'] if nodes else None,  # 使用第一个节点作为根节点
        "nodes": [],
        "lines": []
    }
    
    # 处理节点
    for node in nodes:
        # 使用第一个label的颜色作为节点颜色
        node_color = label_colors[node['labels'][0]] if node['labels'] else generate_random_color()
        # 生成略微不同的边框颜色
        border_r = min(255, random.randint(-20, 20) + int(node_color[5:-1].split(',')[0]))
        border_g = min(255, random.randint(-20, 20) + int(node_color[5:-1].split(',')[1]))
        border_b = min(255, random.randint(-20, 20) + int(node_color[5:-1].split(',')[2]))
        border_color = f"rgba({border_r}, {border_g}, {border_b}, 1)"
        
        new_node = {
            "id": node['id'],
            "text": node['properties'].get('name', ''),
            "color": node_color,
            "borderColor": border_color,
            "data": {
                "description": node['properties'].get('description', ''),
                "labels": node['labels']
            }
        }
        result['nodes'].append(new_node)
    
    # 处理关系
    for rel in relationships:
        rel_color = relationship_colors[rel['label']]
        new_line = {
            "from": rel['start']['id'],     
            "to": rel['end']['id'],
            "text": rel['label'],
            "color": rel_color,
            "data": {
                "type": rel['label'],
                "fromText": rel['start']['properties'].get('id', ''),
                "toText": rel['end']['properties'].get('id', ''),
                "description": rel['properties'].get('description', ''),
                "weight": rel['properties'].get('weight', 1.0)
            }
        }
        result['lines'].append(new_line)
    
    # 写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    input_file = "src/assets/processed_data.jsonl"
    output_file = "src/assets/converted_data.json"
    convert_jsonl_to_json(input_file, output_file) 