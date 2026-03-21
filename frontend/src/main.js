import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import './styles/button-contrast.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.directive('click-outside', {
    mounted(el, binding) {
        el.clickOutsideEvent = function (event) {
            if (!(el === event.target || el.contains(event.target))) {
                binding.value(event);
            }
        };
        document.addEventListener('click', el.clickOutsideEvent);
    },
    unmounted(el) {
        document.removeEventListener('click', el.clickOutsideEvent);
    }
});

app.mount('#app')

// Add 'loaded' class to body or app to trigger FOUC transition
document.getElementById('app').classList.add('loaded')
