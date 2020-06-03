import Vue from 'vue'
import App from './App.vue'
import feather from 'vue-icon'

Vue.use(feather, 'v-icon')
Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')
