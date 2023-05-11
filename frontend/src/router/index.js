import Vue from 'vue'
import VueRouter from 'vue-router'
import PageNotFound from '../views/PageNotFound.vue'

import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import BoardView from '../views/boards/BoardView.vue'
import ListView from '../views/lists/ListView.vue'
import StatsView from '../views/stats/StatsView.vue'
import SettingsView from '../views/SettingsView.vue'
import HomeView from '../views/home/HomeView.vue'
import SignupView from '../views/SignupView.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  // redirect
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignupView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardView,
    children: [
    {
      path: 'home/:userId',
      name: 'home',
      component: HomeView,
      props: (route) => {
        return {
          userId: Number.parseInt(route.params.userId)
        }
      }
    },
    {
      path: 'boards/:userId',
      name: 'boards',
      component: BoardView,
      props: (route) => {
        return {
          userId: Number.parseInt(route.params.userId)
        }
      }
    },
    {
      path: 'lists/:userId/:boardId',
      name: 'lists',
      component: ListView,
      props: (route) => {
        return {
          userId: Number.parseInt(route.params.userId),
          boardId: Number.parseInt(route.params.boardId)
        }
      }
    },
    {
      path: 'stats/:userId',
      name: 'stats',
      component: StatsView,
      props: (route) => {
        return {
          userId: Number.parseInt(route.params.userId)
        }
      }
    },
    {
      path: 'settings/:userId',
      name: 'settings',
      component: SettingsView,
      props: (route) => {
        return {
          userId: Number.parseInt(route.params.userId)
        }
      }
    }
    ] 
  },
  {
    path: '/:catchAll(.*)',
    name: 'PageNotFound',
    component: PageNotFound
  },
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
