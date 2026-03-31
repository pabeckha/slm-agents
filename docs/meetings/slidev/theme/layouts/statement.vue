<template>
  <div class="layout-statement">
    <div class="statement-logo">
      <img src="/theme/assets/dtu-logo-white.svg" alt="DTU" />
    </div>
    <div class="statement-body">
      <slot />
    </div>
    <div class="statement-footer">
      <span>{{ $slidev.configs.date || '' }}</span>
      <span>{{ $slidev.configs.title || '' }}</span>
      <span>{{ $nav.currentPage }} / {{ $nav.total }}</span>
    </div>
  </div>
</template>

<style scoped>
.layout-statement {
  background: var(--dtu-red);
  color: #fff;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.statement-logo {
  padding: 24px 28px;
  flex-shrink: 0;
}

.statement-logo img {
  height: 40px;
  width: auto;
}

.statement-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0 100px;
}

.statement-body :deep(h1) {
  font-size: 2rem;
  font-weight: 700;
  color: #fff;
  border: none;
  margin-bottom: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.5);
}

.statement-body :deep(p) {
  font-size: 1.6rem;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 400;
  max-width: 750px;
}

.statement-body :deep(p em) {
  color: #fff;
  font-style: normal;
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 4px;
}

.statement-footer {
  display: flex;
  justify-content: space-between;
  padding: 16px 80px 18px;
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.4);
}
</style>
