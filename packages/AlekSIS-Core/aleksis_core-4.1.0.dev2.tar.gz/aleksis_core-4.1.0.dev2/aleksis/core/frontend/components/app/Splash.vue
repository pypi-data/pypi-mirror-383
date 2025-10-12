<template>
  <div>
    <div id="logo-container">
      <img :src="'/logo'" alt="Logo" id="logo" width="600" />
    </div>
    <div class="lds-ellipsis">
      <div></div>
      <div></div>
      <div></div>
      <div></div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Splash",
  props: {
    splash: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped>
.progress-container {
  position: fixed;
  top: 10%;
  right: 0;
  left: 0;
  bottom: 10%;
  z-index: 1000;
}

#logo {
  width: 100%;
  max-height: inherit;
}

#logo-container {
  width: min(80vw, 600px);
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  max-height: calc(100vh - 10vh - calc(2 * min(85px, 15vh)));
}

.lds-ellipsis {
  display: inline-block;
  position: absolute;
  bottom: 5vh;
  left: 50%;
  transform: translate(-50%);
  aspect-ratio: 1;
  height: min(15vh, 85px);
}

.lds-ellipsis div {
  position: absolute;
  top: 41.25%;
  width: 16.25%;
  height: 16.25%;
  border-radius: 50%;
  aspect-ratio: 1;
  background: v-bind("$vuetify.theme.current.primary");
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}

.lds-ellipsis div:nth-child(1) {
  left: 10%;
  animation: lds-ellipsis1 0.6s infinite;
}

.lds-ellipsis div:nth-child(2) {
  left: 10%;
  animation: lds-ellipsis2 0.6s infinite;
}

.lds-ellipsis div:nth-child(3) {
  left: 40%;
  animation: lds-ellipsis2 0.6s infinite;
}

.lds-ellipsis div:nth-child(4) {
  left: 70%;
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
    transform: translate(calc(0.3 * min(15vh, 85px)), 0);
  }
}
</style>
