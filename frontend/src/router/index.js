import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ChatPage from '../views/ChatPage.vue'
import CharacterList from '../views/CharacterList.vue'
import SettingsPage from '../views/SettingsPage.vue'

// 定义路由
const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/chat/:characterId?',
    name: 'Chat',
    component: ChatPage,
    props: true
  },
  {
    path: '/characters',
    name: 'CharacterList',
    component: CharacterList
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsPage
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router