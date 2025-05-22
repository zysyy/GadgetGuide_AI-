module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    'plugin:vue/vue3-essential', // 或 vue/vue3-strong/vue3-recommended
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 2020,
  },
  globals: {
    defineProps: 'readonly',
    defineEmits: 'readonly',
    defineExpose: 'readonly',
    withDefaults: 'readonly',
  },
  rules: {
    // 你可以自定义规则
    // 'vue/multi-word-component-names': 0
  }
}
