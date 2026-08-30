import pluginVue from "eslint-plugin-vue";
import tseslint from "typescript-eslint";

export default [
  {
    ignores: ["dist/**", "node_modules/**"],
  },
  // Vue 3 规则集（flat/essential 只含正确性规则，不含风格强制）
  ...pluginVue.configs["flat/essential"],
  {
    // .ts 文件直接用 TS 解析器
    files: ["**/*.ts"],
    languageOptions: {
      parser: tseslint.parser,
    },
  },
  {
    // .vue 由 vue-eslint-parser 解析 SFC，script 部分委托给 TS 解析器
    files: ["**/*.vue"],
    languageOptions: {
      parserOptions: { parser: tseslint.parser },
    },
  },
];
