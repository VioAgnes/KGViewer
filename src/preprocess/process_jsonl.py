import json

def process_jsonl(input_file, output_file):
    # 存储所有节点和关系
    nodes = []
    relationships = []
    
    # 存储需要保留的节点ID
    valid_node_ids = set()
    
    # 第一次遍历：收集所有非Document和Chunk节点
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            if data['type'] == 'node':
                # 如果是Entity节点，移除__Entity__标签
                if '__Entity__' in data['labels']:
                    data['labels'] = [label for label in data['labels'] if label != '__Entity__']
                    # 检查标签数量，如果超过两个则跳过该节点
                    if len(data['labels']) >= 2:
                        continue
                    # 将id改为name
                    if 'id' in data['properties']:
                        data['properties']['name'] = data['properties'].pop('id')
                    nodes.append(data)
                    valid_node_ids.add(data['id'])
                # 如果不是Document和Chunk节点，保留
                elif not any(label in ['__Document__', '__Chunk__'] for label in data['labels']):
                    # 检查标签数量，如果超过两个则跳过该节点
                    if len(data['labels']) >= 2:
                        continue
                    # 将id改为name
                    if 'id' in data['properties']:
                        data['properties']['name'] = data['properties'].pop('id')
                    nodes.append(data)
                    valid_node_ids.add(data['id'])
            else:
                relationships.append(data)
    
    # 第二次遍历：过滤关系
    filtered_relationships = []
    for rel in relationships:
        # 检查关系的起始和结束节点是否都在有效节点ID集合中
        if (rel['start']['id'] in valid_node_ids and 
            rel['end']['id'] in valid_node_ids):
            filtered_relationships.append(rel)
    
    # 写入处理后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        # 写入节点
        for node in nodes:
            f.write(json.dumps(node, ensure_ascii=False) + '\n')
        # 写入关系
        for rel in filtered_relationships:
            f.write(json.dumps(rel, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    input_file = 'src/assets/data.jsonl'
    output_file = 'src/assets/processed_data.jsonl'
    process_jsonl(input_file, output_file)
    print("处理完成！") 