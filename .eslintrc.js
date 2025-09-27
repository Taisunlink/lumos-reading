module.exports = {
  root: true,
  extends: ['@repo/eslint-config'],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
  },
  rules: {
    // 可以在这里添加项目特定的规则
  },
};
