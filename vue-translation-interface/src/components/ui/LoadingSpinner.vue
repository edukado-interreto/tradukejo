<template>
  <div v-if="inline" class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
  <div v-else class="loader" :class="{small: small}"></div>
</template>

<script>
export default {
  props: {
    small: {
      type: Boolean,
      required: false,
      default: false,
    },
    inline: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
}
</script>

<style scoped>
.small {
  transform: scale(.5);
  margin: 2rem auto;
}

.lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 80px;
  height: 1rem;
}
.lds-ellipsis div {
  position: absolute;
  top: 4px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #254E58;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.lds-ellipsis div:nth-child(1) {
  left: 8px;
  animation: lds-ellipsis1 0.6s infinite;
}
.lds-ellipsis div:nth-child(2) {
  left: 8px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(3) {
  left: 32px;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(4) {
  left: 56px;
  animation: lds-ellipsis3 0.6s infinite;
}
@keyframes lds-ellipsis1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes lds-ellipsis3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}
@keyframes lds-ellipsis2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(24px, 0);
  }
}
</style>