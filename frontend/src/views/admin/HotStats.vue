<template>
  <div>
    <h2 class="page-title">热词统计</h2>
    <el-card class="hotstats-card">
      <div class="card-header">
        <span class="card-title">最常被问到的产品/热词</span>
        <span class="card-desc">数据自动统计 · Top 30</span>
      </div>
      <el-table
        :data="hotWords"
        border
        stripe
        class="hotwords-table"
        :header-cell-style="{ background: '#f7faff', fontWeight: 'bold' }"
        :cell-style="{ fontSize: '16px', padding: '8px 0' }"
      >
        <el-table-column label="排名" type="index" width="70">
          <template #default="scope">
            <span :class="'rank rank-' + (scope.$index + 1)">{{ scope.$index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="word" label="热词" />
        <el-table-column prop="count" label="出现次数" width="100"/>
      </el-table>

      <div class="cloud-title">词云可视化</div>
      <div class="cloud-wrap">
        <div ref="cloudRef" class="wordcloud-box"></div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// @ts-ignore
import WordCloud from 'wordcloud'
import { ref, onMounted, nextTick } from 'vue'

// 热词数据
const hotWords = ref<{ word: string, count: number }[]>([])
const cloudRef = ref<HTMLDivElement | null>(null)

// 请求后台热词
async function fetchHotWords() {
  const res = await fetch('http://localhost:8000/admin/hot-words', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  hotWords.value = res.ok ? await res.json() : []
}

// 初始化词云
onMounted(async () => {
  await fetchHotWords()

  // 绘制词云
  nextTick(() => {
    if (cloudRef.value && hotWords.value.length) {
      const data = hotWords.value.slice(0, 30).map(item => [item.word.trim(), item.count])

      WordCloud(cloudRef.value, {
        list: data,
        gridSize: 12,
        // ✅ 修复中文乱码：使用支持中文的字体
        fontFamily: 'PingFang SC, Microsoft YaHei, SimHei, sans-serif',
        // ✅ 避免文字太小
        weightFactor: (count: number) => count * 3,
        minSize: 12,
        color: () => {
          const palette = ['#3573fa', '#f8b74a', '#8eaccb', '#f76560', '#8186a3']
          return palette[Math.floor(Math.random() * palette.length)]
        },
        backgroundColor: 'rgba(255,255,255,0)',
        rotateRatio: 0.1,
        shuffle: true,
        drawOutOfBound: false,
        // ✅ 修复报错：hover 必须是函数或 undefined，不能是布尔值
        hover: undefined,
      })
    }
  })
})
</script>

<style scoped>
.page-title {
  font-size: 1.7em;
  font-weight: bold;
  margin-bottom: 18px;
  color: var(--color-main);
  letter-spacing: 0.5px;
}
.hotstats-card {
  padding: 22px 28px 38px 28px;
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(60,72,90,0.08), 0 1.5px 5px rgba(0,0,0,0.02);
  background: #fff;
  margin: 0 auto;
  max-width: 830px;
}
.card-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 18px;
}
.card-title {
  font-size: 1.24em;
  font-weight: 600;
  color: #3573fa;
  letter-spacing: 1px;
}
.card-desc {
  font-size: 0.98em;
  color: #9ca1ad;
}
.hotwords-table {
  width: 100%;
  margin-bottom: 36px;
  --el-table-border: #e4ebf1;
}
.rank {
  font-weight: bold;
  font-size: 1.07em;
  color: #b3bac9;
  display: inline-block;
  width: 30px;
  text-align: center;
}
.rank-1 { color: #ff9b23; font-size: 1.19em; }
.rank-2 { color: #ffcd52; font-size: 1.15em; }
.rank-3 { color: #3573fa; font-size: 1.14em; }

.cloud-title {
  font-size: 1.1em;
  font-weight: 500;
  color: #3573fa;
  margin-bottom: 10px;
  margin-top: 12px;
  letter-spacing: 0.5px;
}
.cloud-wrap {
  width: 100%;
  display: flex;
  justify-content: center;
}
.wordcloud-box {
  width: 520px;
  height: 210px;
  background: #f8fafc;
  border-radius: 8px;
  margin-bottom: 6px;
  margin-top: 0;
  border: 1px dashed #dde5ed;
}

@media (max-width: 900px) {
  .hotstats-card { max-width: 97vw; }
  .wordcloud-box { width: 98vw; min-width: 260px; }
}
</style>
