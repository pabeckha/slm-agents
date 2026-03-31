<template>
  <div class="layout-section">
    <div class="section-logo">
      <img src="/theme/assets/dtu-logo-white.svg" alt="DTU" />
    </div>
    <div class="section-body">
      <slot />
    </div>
    <div class="section-footer">
      <span>{{ $slidev.configs.date || '' }}</span>
      <span>{{ $slidev.configs.title || '' }}</span>
      <span>{{ $nav.currentPage }} / {{ $nav.total }}</span>
    </div>
  </div>
</template>

<style scoped>
.layout-section {
  background: #990000;
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.section-logo {
  padding: 24px 28px;
  flex-shrink: 0;
}

.section-logo img {
  height: 40px;
  width: auto;
}

.section-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 80px;
}

.section-body :deep(h1) {
  font-size: 2.8rem;
  font-weight: 700;
  color: #fff;
  border: none;
  margin-bottom: 0.2rem;
}

.section-body :deep(h2) {
  font-size: 1.3rem;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.6);
  border: none;
}

.section-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 80px 18px;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
}
</style>
