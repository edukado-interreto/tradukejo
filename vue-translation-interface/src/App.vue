<template>
  <RouterView />
</template>

<style>
.slide-enter-from,
.slide-leave-to {
  transform: scaleY(0.7);
  opacity: 0;
}

.slide-enter-to,
.slide-leave-from {
  transform: scaleY(1);
  opacity: 1;
}

.slide-enter-active,
.slide-leave-active,
.slide-move {
  transition: all 0.15s ease-out;
  transform-origin: top;
}

.jump-enter-from,
.jump-leave-to {
  transform: translateY(-30px);
  opacity: 0;
}

.jump-enter-to,
.jump-leave-from {
  transform: translateY(0);
  opacity: 1;
}

.jump-enter-active {
  transition: all 0.2s cubic-bezier(0.77, 0.06, 0.8, 1.72);
}

.jump-leave-active {
  transition: all 0.2s ease-out;
}
</style>
