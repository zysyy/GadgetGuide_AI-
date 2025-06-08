// src/shims-wordcloud.d.ts
declare module 'wordcloud' {
  // 你可以更详细地声明参数类型（可选），这里只写最基础的 any 兼容所有用法
  const WordCloud: any
  export default WordCloud
}