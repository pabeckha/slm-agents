<template>
  <div class="layout-cover">
    <div class="cover-logo">
      <img src="/theme/assets/dtu-logo-white.svg" alt="DTU" />
    </div>
    <div class="cover-body">
      <slot />
    </div>
    <div class="cover-footer">
      <span>{{ $slidev.configs.date || '' }}</span>
      <span>{{ $slidev.configs.title || '' }}</span>
      <span>{{ $nav.currentPage }} / {{ $nav.total }}</span>
    </div>
  </div>
</template>

<style scoped>
.layout-cover {
  background: #990000;
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0;
}

.cover-logo {
  padding: 24px 28px;
  flex-shrink: 0;
}

.cover-logo img {
  height: 52px;
  width: auto;
}

.cover-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 0 80px 0;
}

.cover-body :deep(h1) {
  font-size: 3.6rem;
  font-weight: 700;
  line-height: 0.95;
  color: #fff;
  border: none;
  margin-bottom: 0.3rem;
}

.cover-body :deep(p) {
  color: rgba(255, 255, 255, 0.65);
  font-size: 1.1rem;
  margin: 0;
}

.cover-body :deep(.meta) {
  margin-top: 2rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.5);
}

.cover-body :deep(.meta strong) {
  color: rgba(255, 255, 255, 0.75);
}

.cover-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 80px 18px;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
}
</style>
