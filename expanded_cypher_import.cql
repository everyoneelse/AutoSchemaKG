// =============================================================================
// Atlas RAG 知识图谱导入脚本 (展开版)
// 数据集: mri_artifacts
// 生成时间: 2025-09-28 07:42:43
// 注意: 此脚本将CSV导入操作展开为具体的CREATE/MATCH命令
// =============================================================================


// =============================================================================
// 约束和索引创建
// =============================================================================

// 创建唯一性约束
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT text_id_unique IF NOT EXISTS FOR (t:Text) REQUIRE t.id IS UNIQUE;

// 创建性能索引
CREATE INDEX entity_name_index IF NOT EXISTS FOR (n:Entity) ON (n.name);
CREATE INDEX concept_name_index IF NOT EXISTS FOR (c:Concept) ON (c.name);
CREATE INDEX entity_type_index IF NOT EXISTS FOR (n:Entity) ON (n.type);

// =============================================================================
// 1. 导入文本节点
// =============================================================================

CREATE (t:Text {id: 'text_001', content: 'MRI artifacts can significantly impact image quality', metadata: '{\'source\': \'medical_paper_1\'}'});
CREATE (t:Text {id: 'text_002', content: 'Motion artifacts are common in pediatric imaging', metadata: '{\'source\': \'medical_paper_2\'}'});
CREATE (t:Text {id: 'text_003', content: 'Susceptibility artifacts occur near metal implants', metadata: '{\'source\': \'medical_paper_3\'}'});

// =============================================================================
// 2. 导入三元组节点 (实体、事件)
// =============================================================================

CREATE (n:Entity {id: 'motion_artifact', name: 'motion_artifact', type: 'artifact', concepts: '[\'motion\', \'artifact\', \'imaging\']', synsets: '[\'motion.n.01\', \'artifact.n.01\']'});
CREATE (n:Entity {id: 'pediatric_patient', name: 'pediatric_patient', type: 'patient', concepts: '[\'pediatric\', \'patient\', \'child\']', synsets: '[\'child.n.01\', \'patient.n.01\']'});
CREATE (n:Entity {id: 'metal_implant', name: 'metal_implant', type: 'implant', concepts: '[\'metal\', \'implant\', \'medical_device\']', synsets: '[\'implant.n.01\', \'metal.n.01\']'});
CREATE (n:Entity {id: 'image_quality', name: 'image_quality', type: 'quality', concepts: '[\'image\', \'quality\', \'assessment\']', synsets: '[\'quality.n.01\', \'image.n.01\']'});

// =============================================================================
// 3. 导入概念节点
// =============================================================================

CREATE (c:Concept {id: 'concept_001', name: 'motion'});
CREATE (c:Concept {id: 'concept_002', name: 'artifact'});
CREATE (c:Concept {id: 'concept_003', name: 'imaging'});
CREATE (c:Concept {id: 'concept_004', name: 'pediatric'});
CREATE (c:Concept {id: 'concept_005', name: 'patient'});
CREATE (c:Concept {id: 'concept_006', name: 'metal'});
CREATE (c:Concept {id: 'concept_007', name: 'implant'});
CREATE (c:Concept {id: 'concept_008', name: 'quality'});

// =============================================================================
// 4. 导入三元组关系
// =============================================================================

MATCH (a:Entity {id: 'motion_artifact'}) MATCH (b:Entity {id: 'image_quality'}) CREATE (a)-[r:RELATES {relation: 'affects', concepts: '[\'affects\', \'impact\']', synsets: '[\'affect.v.01\']'}]->(b);
MATCH (a:Entity {id: 'pediatric_patient'}) MATCH (b:Entity {id: 'motion_artifact'}) CREATE (a)-[r:RELATES {relation: 'experiences', concepts: '[\'experiences\', \'has\']', synsets: '[\'experience.v.01\']'}]->(b);
MATCH (a:Entity {id: 'metal_implant'}) MATCH (b:Entity {id: 'motion_artifact'}) CREATE (a)-[r:RELATES {relation: 'causes', concepts: '[\'causes\', \'produces\']', synsets: '[\'cause.v.01\']'}]->(b);

// =============================================================================
// 5. 导入概念关系
// =============================================================================

MATCH (e:Entity {id: 'motion_artifact'}) MATCH (c:Concept {id: 'concept_001'}) CREATE (e)-[:HAS_CONCEPT]->(c);
MATCH (e:Entity {id: 'motion_artifact'}) MATCH (c:Concept {id: 'concept_002'}) CREATE (e)-[:HAS_CONCEPT]->(c);
MATCH (e:Entity {id: 'pediatric_patient'}) MATCH (c:Concept {id: 'concept_004'}) CREATE (e)-[:HAS_CONCEPT]->(c);
MATCH (e:Entity {id: 'pediatric_patient'}) MATCH (c:Concept {id: 'concept_005'}) CREATE (e)-[:HAS_CONCEPT]->(c);
MATCH (e:Entity {id: 'metal_implant'}) MATCH (c:Concept {id: 'concept_006'}) CREATE (e)-[:HAS_CONCEPT]->(c);
MATCH (e:Entity {id: 'metal_implant'}) MATCH (c:Concept {id: 'concept_007'}) CREATE (e)-[:HAS_CONCEPT]->(c);
MATCH (e:Entity {id: 'image_quality'}) MATCH (c:Concept {id: 'concept_008'}) CREATE (e)-[:HAS_CONCEPT]->(c);

// =============================================================================
// 6. 导入文本关系
// =============================================================================

MATCH (t:Text {id: 'text_001'}) MATCH (e:Entity {id: 'motion_artifact'}) CREATE (t)-[:CONTAINS]->(e);
MATCH (t:Text {id: 'text_001'}) MATCH (e:Entity {id: 'image_quality'}) CREATE (t)-[:CONTAINS]->(e);
MATCH (t:Text {id: 'text_002'}) MATCH (e:Entity {id: 'pediatric_patient'}) CREATE (t)-[:CONTAINS]->(e);
MATCH (t:Text {id: 'text_002'}) MATCH (e:Entity {id: 'motion_artifact'}) CREATE (t)-[:CONTAINS]->(e);
MATCH (t:Text {id: 'text_003'}) MATCH (e:Entity {id: 'metal_implant'}) CREATE (t)-[:CONTAINS]->(e);
MATCH (t:Text {id: 'text_003'}) MATCH (e:Entity {id: 'motion_artifact'}) CREATE (t)-[:CONTAINS]->(e);

// =============================================================================
// 导入统计和验证
// =============================================================================

// 显示节点统计
MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY Count DESC;

// 显示关系统计
MATCH ()-[r]->() RETURN type(r) as RelationType, count(r) as Count ORDER BY Count DESC;

// 显示实体类型分布
MATCH (e:Entity) RETURN e.type as EntityType, count(e) as Count ORDER BY Count DESC;

// 显示概念使用频率 (前20个)
MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept) RETURN c.name as ConceptName, count(e) as EntityCount ORDER BY EntityCount DESC LIMIT 20;

// 显示实体-概念关系示例
MATCH (e:Entity)-[:HAS_CONCEPT]->(c:Concept) RETURN e.name as EntityName, e.type as EntityType, c.name as ConceptName LIMIT 10;
