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

// ── 蓝图主类型 ──

#Blueprint: {
	id:             =~"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
	requirement_id: string
	version:        >0
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
	workflow: {
		name: "高频价格指数计算"
		steps: [
			{
				name: "数据采集"
				from: "category.csv, product.csv, price.csv"
				to:   "oss://cpp-raw/{date}/"
				desc: "上传模拟数据集至对象存储，按日期分区"
			},
			{
				name: "数据预处理"
				from: "oss://cpp-raw/{date}/"
				to:   "clickhouse://staging.cleaned_prices"
				desc: "字段类型适配与转换\n统一时间格式为 YYYY-MM-DD\n统一价格单位为元\n统一分类编码为国标6位码"
				depends: ["数据采集"]
			},
			{
				name: "异常处理"
				from: "clickhouse://staging.cleaned_prices"
				to:   "clickhouse://staging.valid_prices"
				desc: "过滤 price 为空或 <=0 的记录\n标记价格波动超过 3σ 的异常点"
				depends: ["数据预处理"]
			},
			{
				name: "分类加权平均"
				from: "clickhouse://staging.valid_prices"
				to:   "clickhouse://staging.category_daily_avg"
				desc: "按 category_id + date 分组\n计算销量加权平均价格"
				depends: ["异常处理"]
			},
			{
				name: "链式指数计算"
				from: "clickhouse://staging.category_daily_avg"
				to:   "clickhouse://mart.daily_price_index"
				desc: "基期指数 = 100\n当日指数 = 上期指数 × (1 + 环比变化率)\nGROUP BY category_id ORDER BY date"
				depends: ["分类加权平均"]
			},
			{
				name: "可视化"
				from: "clickhouse://mart.daily_price_index"
				to:   "output/daily_index_trend.png"
				desc: "Python matplotlib 绘制日度指数趋势图"
				depends: ["链式指数计算"]
			},
		]
	}
	status: "submitted"
	created_at: "2026-06-22T09:00:00+08:00"
	updated_at: "2026-06-22T10:00:00+08:00"
}
