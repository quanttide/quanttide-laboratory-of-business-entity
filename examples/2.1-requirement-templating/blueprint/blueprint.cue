// ── 基础类型 ──

#Timestamp: =~"^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:\\d{2}$"

#Step: {
	name:    string
	from:    string
	to:      string
	desc:    string
	depends?: [...string]
}

#Pipeline: {
	name:  string
	steps: [...#Step]
}

#TimelineEntry: {
	action:    "submit" | "confirm" | "reject" | "resubmit"
	actor:     string
	timestamp: #Timestamp
	note?:     string
}

#Status: "draft" | "submitted" | "confirmed" | "rejected"

// ── 数据模型类型 ──

#CategoryTable: {
	table:   "category"
	fields: [
		{name: "code";        type: "INT";           constraint: "PRIMARY KEY, NOT NULL"; comment: "分类编号"},
		{name: "name";        type: "VARCHAR(50)";    constraint: "NOT NULL";            comment: "分类名称"},
		{name: "weight";      type: "DECIMAL(8,4)";   constraint: "—";                   comment: "CPI 计算权重"},
		{name: "hierarchy";   type: "INT";            constraint: "NOT NULL";            comment: "分类层级: 1=一级, 2=二级, 3=三级"},
		{name: "parent";      type: "INT";            constraint: "FOREIGN KEY";         comment: "父分类编号, 顶级为 NULL"},
	]
}

#ProductTable: {
	table:   "product"
	fields: [
		{name: "product_id";  type: "INT";           constraint: "PRIMARY KEY, NOT NULL"; comment: "商品唯一标识"},
		{name: "category_id"; type: "INT";           constraint: "FOREIGN KEY, NOT NULL"; comment: "所属叶子分类编号"},
		{name: "name";        type: "VARCHAR(50)";    constraint: "—";                   comment: "商品名称"},
		{name: "weight";      type: "FLOAT";          constraint: "—";                   comment: "分类内权重, 同分类和=1"},
		{name: "price";       type: "DECIMAL(12,2)";  constraint: ">= 0";                comment: "商品基础价格（元）"},
	]
}

#PriceTable: {
	table:   "price"
	fields: [
		{name: "date";        type: "DATE";           constraint: "PRIMARY KEY, NOT NULL"; comment: "价格日期"},
		{name: "product_id";  type: "INT";            constraint: "PRIMARY KEY, FOREIGN KEY, NOT NULL"; comment: "商品编号"},
		{name: "price";       type: "DECIMAL(12,2)";  constraint: ">= 0";                comment: "当日价格（元）"},
	]
}

#DataModel: {
	category: #CategoryTable
	product:  #ProductTable
	price:    #PriceTable
}

// ── 配置契约类型 ──

#EnvironmentConfig: {
	local: {
		storage:   "MinIO (localhost:9000)"
		database:  "ClickHouse 本地实例"
		ssl:       false
		cert_verify: false
	}
	prod: {
		storage:   "阿里云 OSS"
		database:  "阿里云 ClickHouse"
		ssl:       true
		cert_verify: true
	}
}

#OSSConfig: {
	endpoint: string
	bucket:   string
	access_key: string  // 生产环境通过环境变量注入
}

#ClickHouseConfig: {
	host:            string
	port:            int
	user:            string
	password:        string
	connect_timeout: int    // 生产 30s, 本地 60s
	max_execution:   int    // 180s
}

#SimulationParams: {
	days:               int
	categories:         [...string]
	items_per_category: int
	category_weights:   [string]: float
}

#AlgorithmConfig: {
	base_mode: "auto" | "monthly" | "fixed"
	index_type: "cavallo" | "tmall"
	chain_mode: "chain"
}

#DataFilePaths: {
	category:  "data/categories.csv"
	product:   "data/products.csv"
	daily_price: "data/daily_price/daily_prices_YYYYMMDD.csv"
}

#StorageContract: {
	oss: #OSSConfig
	clickhouse: {
		connector: #ClickHouseConfig
		ddl: {
			category_engine: "MergeTree ORDER BY category_id"
			item_engine:     "MergeTree ORDER BY item_id"
			price_engine:    "MergeTree ORDER BY (date, item_id)"
		}
	}
	file_paths: #DataFilePaths
}

// ── 蓝图主类型 ──

#Blueprint: {
	id:             =~"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
	requirement_id: string
	version:        >0
	data_model:     #DataModel
	environment:    #EnvironmentConfig
	oss:            #OSSConfig
	clickhouse:     #ClickHouseConfig
	simulation:     #SimulationParams
	algorithm:      #AlgorithmConfig
	storage:        #StorageContract
	workflow:       #Pipeline
	status:         #Status
	timeline?:      [...#TimelineEntry]
	created_at:     #Timestamp
	updated_at:     #Timestamp
}

// ── 实例数据 ──

pseudocode: #Blueprint & {
	id:             "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
	requirement_id: "req-2026-001"
	version:        1

	data_model: {
		category: {
			table: "category"
			fields: [
				{name: "code";      type: "INT";          constraint: "PRIMARY KEY, NOT NULL"; comment: "分类编号"}
				{name: "name";      type: "VARCHAR(50)";   constraint: "NOT NULL";            comment: "分类名称"}
				{name: "weight";    type: "DECIMAL(8,4)";  constraint: "—";                   comment: "CPI 计算权重"}
				{name: "hierarchy"; type: "INT";           constraint: "NOT NULL";            comment: "分类层级: 1=一级, 2=二级, 3=三级"}
				{name: "parent";    type: "INT";           constraint: "FOREIGN KEY";         comment: "父分类编号, 顶级为 NULL"}
			]
		}
		product: {
			table: "product"
			fields: [
				{name: "product_id";  type: "INT";          constraint: "PRIMARY KEY, NOT NULL"; comment: "商品唯一标识"}
				{name: "category_id"; type: "INT";          constraint: "FOREIGN KEY, NOT NULL"; comment: "所属叶子分类编号"}
				{name: "name";        type: "VARCHAR(50)";   constraint: "—";                   comment: "商品名称"}
				{name: "weight";      type: "FLOAT";         constraint: "—";                   comment: "分类内权重, 同分类和=1"}
				{name: "price";       type: "DECIMAL(12,2)"; constraint: ">= 0";                comment: "商品基础价格（元）"}
			]
		}
		price: {
			table: "price"
			fields: [
				{name: "date";       type: "DATE";          constraint: "PRIMARY KEY, NOT NULL"; comment: "价格日期"}
				{name: "product_id"; type: "INT";           constraint: "PRIMARY KEY, FOREIGN KEY, NOT NULL"; comment: "商品编号"}
				{name: "price";      type: "DECIMAL(12,2)"; constraint: ">= 0";                comment: "当日价格（元）"}
			]
		}
	}

	environment: {
		local: {
			storage:   "MinIO (localhost:9000)"
			database:  "ClickHouse 本地实例"
			ssl:       false
			cert_verify: false
		}
		prod: {
			storage:   "阿里云 OSS"
			database:  "阿里云 ClickHouse"
			ssl:       true
			cert_verify: true
		}
	}

	oss: {
		endpoint: "oss-cn-hangzhou.aliyuncs.com"
		bucket:   "prod-ecommerce-data"
		access_key: "$OSS_ACCESS_KEY_ID"
	}

	clickhouse: {
		host:            "cc-bp143310x5229s4k4.public.clickhouse.ads.aliyuncs.com"
		port:            3306
		user:            "root1"
		password:        "$CLICKHOUSE_PASSWORD"
		connect_timeout: 30
		max_execution:   180
	}

	simulation: {
		days:               365
		categories:         ["食品", "家居", "数码", "服饰"]
		items_per_category: 50
		category_weights: {
			"食品": 0.4
			"家居": 0.2
			"数码": 0.2
			"服饰": 0.2
		}
	}

	algorithm: {
		base_mode:  "auto"
		index_type: "cavallo"
		chain_mode: "chain"
	}

	storage: {
		oss: {
			endpoint: "oss-cn-hangzhou.aliyuncs.com"
			bucket:   "prod-ecommerce-data"
			access_key: "$OSS_ACCESS_KEY_ID"
		}
		clickhouse: {
			connector: {
				host:            "cc-bp143310x5229s4k4.public.clickhouse.ads.aliyuncs.com"
				port:            3306
				user:            "root1"
				password:        "$CLICKHOUSE_PASSWORD"
				connect_timeout: 30
				max_execution:   180
			}
			ddl: {
				category_engine: "MergeTree ORDER BY category_id"
				item_engine:     "MergeTree ORDER BY item_id"
				price_engine:    "MergeTree ORDER BY (date, item_id)"
			}
		}
		file_paths: {
			category:  "data/categories.csv"
			product:   "data/products.csv"
			daily_price: "data/daily_price/daily_prices_YYYYMMDD.csv"
		}
	}

	workflow: {
		name: "高频价格指数计算"
		steps: [
			{
				name: "数据生成"
				from: "模拟参数配置"
				to:   "data/categories.csv, data/products.csv, data/daily_price/daily_prices_*.csv"
				desc: "基于分类/商品/价格三级模型生成模拟数据\n四类权重 0.4/0.2/0.2/0.2, 每类 50 商品\n价格在基础价 ±30% 范围内随机\n每日 1%~2% 商品更替模拟真实货架\n生成 365 天每日价格文件"
			},
			{
				name: "数据导入"
				from: "data/categories.csv, data/products.csv, data/daily_price/"
				to:   "对象存储 + ClickHouse (category/price 表)"
				desc: "上传 CSV 至 OSS/MinIO\n创建 ClickHouse 三表 (MergeTree)\n批量写入数据\n本地用 MinIO, 生产用阿里云 OSS"
				depends: ["数据生成"]
			},
			{
				name: "数据清洗"
				from: "ClickHouse 原始数据表"
				to:   "ClickHouse 清洗后数据表"
				desc: "过滤空价格和零/负价格\n日期转换为 Date 类型\n商品 ID 统一大写去空格\n分类权重裁剪至 [0,1] 并归一化\n价格保留 Decimal(12,2) 精度"
				depends: ["数据导入"]
			},
			{
				name: "价格指数计算"
				from: "ClickHouse 清洗后数据表"
				to:   "data/cavallo_index.csv, data/tmall_index.csv"
				desc: "Cavallo: 几何平均法, 报告期/基期比率几何平均 ×100\nTmall: 加权平均法, 分类平均价 × 权重聚合\n三种基期模式: auto/monthly/fixed\n链式: 每期基于上期环比推算"
				depends: ["数据清洗"]
			},
			{
				name: "可视化"
				from: "data/*_index.csv"
				to:   "output/index_trend.png 或 .html"
				desc: "matplotlib 静态图或 plotly 交互图\n日期横轴, 指数值纵轴\n折线图展示日度 CPI 趋势\n生产环境可接入 QuickBI"
				depends: ["价格指数计算"]
			},
			{
				name: "测试与验证"
				from: "手工构造的小规模 CSV"
				to:   "测试报告"
				desc: "单元测试: 数据生成器/CPI 计算器\n集成测试: 商品覆盖率 ≥80%\n异常过滤准确率 ≥95% (可选)"
				depends: ["数据生成", "数据导入", "数据清洗", "价格指数计算", "可视化"]
			},
			{
				name: "文档与报告"
				from: "全部前置步骤产出"
				to:   "设计文档 + 实践报告"
				desc: "设计文档: 需求分析/表设计/Python 逻辑/SQL 逻辑\n实践报告: 需求分析/表设计/SQL 分析/代码设计/截图/心得"
				depends: ["测试与验证"]
			},
		]
	}
	status: "submitted"
	created_at: "2026-06-22T09:00:00+08:00"
	updated_at: "2026-06-22T10:00:00+08:00"
}
