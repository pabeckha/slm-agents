<template>
  <div class="layout-default">
    <div class="default-header">
      <img class="header-logo" src="/theme/assets/dtu-logo-red.svg" alt="DTU" />
    </div>
    <div class="default-body">
      <slot />
    </div>
    <div class="default-footer">
      <span>{{ $slidev.configs.date || '' }}</span>
      <span class="footer-title">{{ $slidev.configs.title || '' }}</span>
      <span>{{ $nav.currentPage }}</span>
    </div>
  </div>
</template>

<style scoped>
.layout-default {
  background: #fff;
  color: #000;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.default-header {
  padding: 20px 28px 0;
  flex-shrink: 0;
}

.header-logo {
  height: 36px;
  width: auto;
}

.default-body {
  flex: 1;
  padding: 8px 80px 16px 148px;
  overflow: hidden;
}

.default-body :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #990000;
  border-bottom: 2px solid #990000;
  padding-bottom: 0.35rem;
  margin-bottom: 1rem;
}

.default-body :deep(ul) {
  list-style: disc;
  padding-left: 1.4em;
  margin-bottom: 0.5rem;
}

.default-body :deep(ol) {
  list-style: decimal;
  padding-left: 1.4em;
  margin-bottom: 0.5rem;
}

.default-body :deep(li) {
  font-size: 0.88rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

.default-body :deep(table) {
  width: 100%;
  font-size: 0.8rem;
  border-collapse: collapse;
}

.default-body :deep(th) {
  background: #990000;
  color: #fff;
  padding: 0.4rem 0.6rem;
  text-align: left;
  font-weight: 700;
  font-size: 0.75rem;
}

.default-body :deep(td) {
  padding: 0.35rem 0.6rem;
  border-bottom: 1px solid #e5e5e5;
}

.default-body :deep(tr:nth-child(even) td) {
  background: #fafafa;
}

.default-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 80px 12px;
  font-size: 0.7rem;
  color: #999;
  border-top: 1px solid #e5e5e5;
  flex-shrink: 0;
}

.footer-title {
  flex: 1;
  text-align: right;
  padding-right: 16px;
}
</style>
